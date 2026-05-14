from collections import defaultdict
from apps.courses.models import Node, NodeLink
from apps.records.models import Progress, Attempt

# On charge les relations une seule fois en mémoire pour éviter les requêtes N+1
# C'est beaucoup plus performant pour le dashboard.
def build_node_tree_in_memory():
    # Récupère tous les noeuds et les indexes par ID
    all_nodes = {node.id: node for node in Node.objects.all()}
    
    # Construit un dictionnaire parent -> liste d'enfants
    links_by_parent = defaultdict(list) # dictionnaire qui renvoie une liste vide 
                                        # plutôt qu'une KeyError quand la clé n'exsite pas
    for link in NodeLink.objects.all():
        links_by_parent[link.parent_id].append(link.child_id)
        
    return all_nodes, links_by_parent

def get_descendant_leaves(root_node_id, all_nodes, links_by_parent):
    """
    Parcourt récursivement l'arbre en mémoire pour trouver les feuilles 
    (Leçons, Quiz, Exercices) d'un noeud donné.
    """
    leaves = []
    visited = set()
    
    def traverse(node_id):
        if node_id in visited:
            return
        visited.add(node_id)
        
        node = all_nodes.get(node_id)
        if not node:
            return
            
        children_ids = links_by_parent.get(node_id) # Le defaultdict renverra [] si pas d'enfant
        if not children_ids:
            # Si pas d'enfant et que c'est un type "feuille", on l'ajoute
            if node.type in [Node.Type.LESSON, Node.Type.QUIZ, Node.Type.EXERCISE]:
                leaves.append(node)
        else:
            for child_id in children_ids:
                traverse(child_id)
                
    traverse(root_node_id)
    return leaves

def get_descendant_leaves_map(root_nodes):
    """
    Prend une liste de noeuds (ex: tous les chapitres) et retourne
    un dictionnaire associant chaque noeud à ses feuilles.
    """
    all_nodes, links_by_parent = build_node_tree_in_memory()
    leaves_map = {}
    for root in root_nodes:
        leaves_map[root.id] = get_descendant_leaves(root.id, all_nodes, links_by_parent)
    return leaves_map

def compute_simple_stats(leaf_nodes, progresses_by_node_id):
    """
    Calcule les statistiques de base pour un noeud ou un ensemble de noeuds.
    """
    total = len(leaf_nodes)
    completed = 0
    in_progress = 0
    
    # Itérer sur les leafs plutôt que sur les progrès n'augmente pas la complexité
    # car il y a forcément besoin de compter toutes les leafs pour avoir accès aux "not_started" et "total"
    for leaf in leaf_nodes:
        progress = progresses_by_node_id.get(leaf.id)
        if progress:
            if progress.status == Progress.Status.COMPLETED:
                completed += 1
            elif progress.status == Progress.Status.IN_PROGRESS:
                in_progress += 1
                
    return {
        "completed": completed,
        "in_progress": in_progress,
        "not_started": total - completed - in_progress,
        "total": total
    }

def get_empty_detailed_stat_block():
    # Structure de base pour un type de noeud (lesson, quiz, etc)
    return {
        "completed": {"easy": 0, "medium": 0, "hard": 0, "total": 0},
        "in_progress": {"easy": 0, "medium": 0, "hard": 0, "total": 0},
        "not_started": {"easy": 0, "medium": 0, "hard": 0, "total": 0},
        "total": 0
    }

def compute_detailed_stats(leaf_nodes, progresses_by_node_id):
    """
    Génère les statistiques détaillées (par type, statut, et difficulté).
    """
    stats = {
        "lesson": get_empty_detailed_stat_block(),
        "quiz": get_empty_detailed_stat_block(),
        "exercise": get_empty_detailed_stat_block(),
        "total": 0
    }
    
    # Mapping entre le type dans la BDD et la clé du JSON
    type_mapping = {
        Node.Type.LESSON: "lesson",
        Node.Type.QUIZ: "quiz",
        Node.Type.EXERCISE: "exercise"
    }
    
    difficulty_mapping = {
        Node.Difficulty.EASY: "easy",
        Node.Difficulty.MEDIUM: "medium",
        Node.Difficulty.HARD: "hard",    }
    
    # Itérer sur les leafs plutôt que sur les progrès n'augmente pas la complexité
    # car il y a forcément besoin de compter toutes les leafs pour avoir accès aux "not_started" et "total"
    for leaf in leaf_nodes:
        node_type_key = type_mapping.get(leaf.type)
        if not node_type_key:
            continue
            
        difficulty_key = difficulty_mapping.get(leaf.difficulty, "easy") # "easy" Valeur par défaut si non spécifié
        
        # Déterminer le statut
        status_key = "not_started"
        progress = progresses_by_node_id.get(leaf.id)
        if progress:
            if progress.status == Progress.Status.COMPLETED:
                status_key = "completed"
            elif progress.status == Progress.Status.IN_PROGRESS:
                status_key = "in_progress"
                
        # On met à jour le bloc
        stats[node_type_key][status_key][difficulty_key] += 1
        stats[node_type_key][status_key]["total"] += 1
        stats[node_type_key]["total"] += 1
        stats["total"] += 1
        
    return stats

def compute_timeline(progresses_by_node_id, attempts_by_node_id):
    """
    Construit l'historique d'activité jour par jour (timeline).
    """

    # On utilise un defaultdict comme ça on peut directement incrémenter, 
    # pas besoin de vérifier si la clé existe et de faire des disjonctions de cas
    timeline = defaultdict(lambda: {"new_in_progress": 0, "new_completed": 0, "attempts": 0}) 
    
    # On parcourt les progressions pour trouver les passages à IN_PROGRESS ou COMPLETED
    for node_id, progress in progresses_by_node_id.items():
        if progress.in_progress_at:
            day_str = progress.in_progress_at.date().isoformat()
            timeline[day_str]["new_in_progress"] += 1
        if progress.completed_at:
            day_str = progress.completed_at.date().isoformat()
            timeline[day_str]["new_completed"] += 1
                
    # On ajoute les essais (attempts)
    for node_id, attempts in attempts_by_node_id.items():
        for attempt in attempts:
            day_str = attempt.date.date().isoformat()
            timeline[day_str]["attempts"] += 1
                
    return dict(timeline)
