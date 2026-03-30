import os
import json
import re
from pathlib import Path
from django.contrib.auth import get_user_model
from django.db import transaction

# Ces lignes permettent d'importer les modèles même si le script est lancé via le shell
from apps.courses.models import Node, NodeNode

User = get_user_model()

BASE_DIR = Path('/app/courses_data')

ROOT_MAP = {
    "seconde": {"grade_level": Node.GradeLevel.SECONDE, "subject": Node.Subject.MATHS, "title": "Mathématiques Seconde"},
    "premiere/maths": {"grade_level": Node.GradeLevel.PREMIERE, "subject": Node.Subject.MATHS, "title": "Mathématiques Première"},
    "premiere/nsi": {"grade_level": Node.GradeLevel.PREMIERE, "subject": Node.Subject.COMPUTER_SCIENCE, "title": "NSI Première"},
    "premiere/physique": {"grade_level": Node.GradeLevel.PREMIERE, "subject": Node.Subject.PHYSICS, "title": "Physique Première"},
    "terminale/maths": {"grade_level": Node.GradeLevel.TERMINALE, "subject": Node.Subject.MATHS, "title": "Mathématiques Terminale"},
    "terminale/nsi": {"grade_level": Node.GradeLevel.TERMINALE, "subject": Node.Subject.COMPUTER_SCIENCE, "title": "NSI Terminale"},
    "terminale/physique": {"grade_level": Node.GradeLevel.TERMINALE, "subject": Node.Subject.PHYSICS, "title": "Physique Terminale"},
}

def extract_order(name, prefix):
    match = re.search(fr'{prefix}(\d+)', name)
    return int(match.group(1)) if match else None

def get_or_create_codeclique_user():
    user, created = User.objects.get_or_create(username="codeclique")
    user.set_unusable_password()
    if not user.role:
        user.role = User.Role.ADMIN
    user.save()
    return user

def process_file_content(path, node_type, base_name):
    # Selon le node_type, on lit différents fichiers
    content = {}
    json_path = path / f"{base_name}.json"
    md_path = path / f"{base_name}.md"
    py_path = path / f"{base_name}.py"
    
    json_data = {}
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            
    if node_type == Node.Type.LESSON:
        md_text = ""
        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                md_text = f.read()
        content = {"content": md_text}

    elif node_type == Node.Type.EXERCISE:
        content = {}
        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                content["content"] = f.read()
                
        if py_path.exists():
            import subprocess
            try:
                result = subprocess.run(
                    ["python", str(py_path)], 
                    capture_output=True, 
                    text=True, 
                    input="",
                    timeout=2
                )
                content["answer"] = result.stdout.strip()
            except subprocess.TimeoutExpired:
                print(f"      Le script {py_path.name} contient une boucle infinie ou a expiré.")
                content["answer"] = ""
            except Exception as e:
                print(f"      Erreur lors de l'exécution du script {py_path.name} : {e}")
        
    elif node_type == Node.Type.QUIZ:
        # Le contenu du quiz est une liste de questions
        if "content" in json_data:
            content = json_data.pop("content")
        else:
            content = []
            
    return json_data, content

def sync_courses():
    codeclique_user = get_or_create_codeclique_user()
    
    # 1. Supprimer tous les cours appartenant à l'utilisateur codeclique
    print("Suppression des cours existants pour l'utilisateur codeclique...")
    Node.objects.filter(owner=codeclique_user).delete()
    
    # 2. Traiter les dossiers racines valides
    for root_rel_path, meta in ROOT_MAP.items():
        root_dir = BASE_DIR / root_rel_path
        if not root_dir.exists():
            print(f"Le dossier '{root_dir}' n'existe pas, ignoré.")
            continue
            
        print(f"Traitement du programme : '{root_rel_path}'")
        
        # Créer le nœud SYLLABUS (Programme)
        syllabus_node = Node.objects.create(
            owner=codeclique_user,
            type=Node.Type.SYLLABUS,
            public=True,
            title=meta["title"],
            grade_level=meta["grade_level"],
            subject=meta["subject"],
            difficulty=None,
            content=""
        )
        
        # Chercher les chapitres
        for item in root_dir.iterdir():
            if item.is_dir() and item.name.startswith("chap"):
                order = extract_order(item.name, "chap")
                process_chapter(item, syllabus_node, order, meta, codeclique_user)

def read_json_if_exists(filepath):
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def process_chapter(path, parent_node, order, meta, user):
    chap_json = read_json_if_exists(path / "chap.json")
    if not chap_json or not chap_json.get("title") or "difficulty" not in chap_json:
        print(f"  Chapitre ignoré '{path.name}' : chap.json manquant ou incomplet (titre vide)")
        return
    
    title = chap_json.get("title")
    description = chap_json.get("description", "")
    difficulty = chap_json.get("difficulty")
    
    print(f"  Création du chapitre : {title} (Ordre: {order})")
    chapter_node = Node.objects.create(
        owner=user,
        type=Node.Type.CHAPTER,
        public=True,
        title=title,
        description=description,
        grade_level=meta["grade_level"],
        subject=meta["subject"],
        difficulty=difficulty,
        content=""
    )
    
    # Lier au programme
    NodeNode.objects.create(parent=parent_node, child=chapter_node, order_index=order)
    
    # Traiter le contenu du chapitre (sections, leçons, exercices, quiz)
    process_children(path, chapter_node, meta, user)

def process_section(path, parent_node, order, meta, user):
    sec_json = read_json_if_exists(path / "sec.json")
    if not sec_json or not sec_json.get("title") or "difficulty" not in sec_json:
        print(f"    Section ignorée '{path.name}' : sec.json manquant ou incomplet (titre vide)")
        return
    
    title = sec_json.get("title")
    description = sec_json.get("description", "")
    difficulty = sec_json.get("difficulty")
    
    print(f"    Création de la section : {title} (Ordre: {order})")
    section_node = Node.objects.create(
        owner=user,
        type=Node.Type.SECTION,
        public=True,
        title=title,
        description=description,
        grade_level=meta["grade_level"],
        subject=meta["subject"],
        difficulty=difficulty,
        content=""
    )
    
    # Lier au chapitre
    NodeNode.objects.create(parent=parent_node, child=section_node, order_index=order)
    
    # Traiter le contenu de la section
    process_children(path, section_node, meta, user)

def process_children(parent_path, parent_node, meta, user):
    # Trouver tous les éléments qui sont :
    # - un dossier de section (secX)
    # - un fichier json de leçon (lessonX), d'exercice (exX) ou de quiz (quizX)
    items = []
    seen = set()
    
    for item in parent_path.iterdir():
        if item.is_dir() and item.name.startswith("sec"):
            order = extract_order(item.name, "sec")
            items.append((order, "section", item, item.name))
        
        elif item.is_file() and item.suffix == ".json":
            base_name = item.stem
            
            # Ignorer les fichiers de configuration génériques
            if base_name in ["chap", "sec"]:
                continue
                
            if base_name in seen:
                continue
            seen.add(base_name)
            
            if base_name.startswith("lesson"):
                order = extract_order(base_name, "lesson")
                items.append((order, "lesson", parent_path, base_name))
            elif base_name.startswith("ex"):
                order = extract_order(base_name, "ex")
                items.append((order, "ex", parent_path, base_name))
            elif base_name.startswith("quiz"):
                order = extract_order(base_name, "quiz")
                items.append((order, "quiz", parent_path, base_name))
                
    # Trier les enfants par ordre
    items.sort(key=lambda x: (x[0] if x[0] is not None else 999))
    
    for order, item_type, path, name in items:
        if item_type == "section":
            process_section(path, parent_node, order, meta, user)
        else:
            # Traiter les leçons, exercices et quiz
            node_type_mapping = {
                "lesson": Node.Type.LESSON,
                "ex": Node.Type.EXERCISE,
                "quiz": Node.Type.QUIZ
            }
            node_type = node_type_mapping[item_type]
            
            json_data, content = process_file_content(path, node_type, name)
            
            item_name_fr = {"lesson": "Leçon", "ex": "Exercice", "quiz": "Quiz"}.get(item_type, item_type)
            
            if not json_data or not json_data.get("title") or "difficulty" not in json_data:
                print(f"      {item_name_fr} ignoré(e) '{name}' : {name}.json manquant ou incomplet (titre vide)")
                continue
                
            title = json_data.get("title")
            difficulty = json_data.get("difficulty")
            
            print(f"      Création - {item_name_fr} : {title} (Ordre: {order})")
            
            leaf_node = Node.objects.create(
                owner=user,
                type=node_type,
                public=True,
                title=title,
                description=json_data.get("description", ""),
                grade_level=meta["grade_level"],
                subject=meta["subject"],
                difficulty=difficulty,
                content=content
            )
            
            NodeNode.objects.create(parent=parent_node, child=leaf_node, order_index=order)

with transaction.atomic():
    sync_courses()
print("Le script de remplissage de la base de données s'est terminé avec succès.")
