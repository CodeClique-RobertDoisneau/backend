import os
import json
import django
from pathlib import Path

# # Configuration de l'environnement Django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'codeclique.settings')
# django.setup()

from apps.courses.models import Chapter, Section, Item, GradeLevel, ItemType

# --- CONFIGURATION ---
# Chemin vers ton dossier 'courses' (relatif ou absolu)
# Modifie ceci pour pointer vers ton dossier local ou monté dans Docker
COURSES_DIR = Path('/app/courses_data')  # Si tu montes le volume dans Docker


# Ou en local pour tester : Path('../courses')

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_markdown(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_grade_level(value):
    """Convertit la string du JSON en choix du modèle (insensible à la casse)"""
    value = value.upper()
    if value in GradeLevel.values:
        return value
    # Mapping de secours si nécessaire
    mapping = {
        '2NDE': GradeLevel.SECONDE,
        '1ERE': GradeLevel.PREMIERE,
        'TERM': GradeLevel.TERMINALE
    }
    return mapping.get(value, GradeLevel.SECONDE)


def get_item_type(value):
    """Convertit le type d'item"""
    value = value.upper()
    if value in ItemType.values:
        return value
    return ItemType.LESSON  # Valeur par défaut


def process_item(item_json_path, section_obj):
    """Traite un fichier itemX.json et son itemX.md associé"""
    base_path = item_json_path.with_suffix('')  # Enlève .json
    md_path = base_path.with_suffix('.md')  # Ajoute .md

    data = load_json(item_json_path)
    content = load_markdown(md_path)

    print(f"    - Traitement Item: {data.get('title', base_path.name)}")

    item, created = Item.objects.update_or_create(
        title=data['title'],
        defaults={
            'item_type': get_item_type(data.get('item_type', 'LESSON')),
            'difficulty': data.get('difficulty', 1),
            'content': content
        }
    )

    # Lier l'item à la section (Relation ManyToMany)
    item.sections.add(section_obj)


def process_section(section_dir, chapter_obj):
    """Traite un dossier section (sec1, sec2...)"""
    sec_json_path = section_dir / 'sec.json'
    if not sec_json_path.exists():
        return

    data = load_json(sec_json_path)
    print(f"  > Traitement Section: {data.get('title')}")

    section, created = Section.objects.update_or_create(
        title=data['title'],
        defaults={
            'description': data.get('description', ''),
            'difficulty': data.get('difficulty', 1)
        }
    )

    # Lier la section au chapitre (Relation ManyToMany)
    section.chapters.add(chapter_obj)

    # Chercher les items (item*.json)
    # On trie pour garder un ordre logique (item1, item2...)
    item_files = sorted(section_dir.glob('item*.json'))
    for item_file in item_files:
        process_item(item_file, section)


def process_chapter(chapter_dir):
    """Traite un dossier qui contient un chap.json"""
    chap_json_path = chapter_dir / 'chap.json'
    data = load_json(chap_json_path)

    print(f"Traitement Chapitre: {data.get('title')}")

    chapter, created = Chapter.objects.update_or_create(
        title=data['title'],
        defaults={
            'description': data.get('description', ''),
            'grade_level': get_grade_level(data.get('grade_level', 'SECONDE'))
        }
    )

    # Chercher les sous-dossiers qui pourraient être des sections
    # On suppose que tout dossier contenant 'sec.json' est une section
    for child in chapter_dir.iterdir():
        if child.is_dir() and (child / 'sec.json').exists():
            process_section(child, chapter)


def scan_directory(root_dir):
    """Parcours récursif pour trouver les chapitres"""
    print(f"Scan du dossier : {root_dir.resolve()}")

    # On utilise os.walk pour traverser toute l'arborescence
    for root, dirs, files in os.walk(root_dir):

        dirs.sort()

        path = Path(root)
        if 'chap.json' in files:
            # Si on trouve chap.json, c'est un Chapitre
            process_chapter(path)
            # On peut décider de ne pas descendre plus bas via os.walk
            # si process_chapter gère déjà les sous-dossiers sections.
            # Mais ici on laisse continuer au cas où il y aurait des structures imbriquées.


if not COURSES_DIR.exists():
    print(f"ERREUR: Le dossier {COURSES_DIR} n'existe pas.")
else:
    scan_directory(COURSES_DIR)
    print("Importation terminée !")