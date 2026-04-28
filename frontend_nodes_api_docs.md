# Documentation API - Endpoints, Filtres et Tris

Ce document recense de manière exhaustive les paramètres d'URL (filtres exacts, recherche et tri) et les permissions pour chaque ressource de l'application `courses`.

---

## 1. Modèle `Node` (Nœuds de cours)
**Endpoint principal :** `/api/nodes/`

### 🔒 Permissions
> [!NOTE]
> La liste (`GET /api/nodes/`) est silencieusement filtrée en fonction des accès de l'utilisateur.

* **Lecture (GET)** : L'utilisateur doit être admnistrateur **OU** le nœud est public **OU** l'utilisateur est le propriétaire (`owner`) **OU** l'utilisateur fait partie d'un groupe auquel le nœud est assigné.
* **Création (POST)** : Réservée aux professeurs (rôle `TEACHER`) et aux administrateurs.
* **Modification / Suppression (PUT, PATCH, DELETE)** : Réservée au propriétaire (`owner`) du nœud ou à un administrateur.

### 🔍 Paramètres d'URL disponibles
Vous pouvez combiner plusieurs filtres dans l'URL pour affiner les résultats.

| Paramètre | Fonctionnalité | Champs supportés | Exemple |
|---|---|---|---|
| `?champ=valeur` | **Filtrage exact** | `type`, `subject`, `grade_level`, `difficulty`, `public`, `owner` | `?type=QU&difficulty=2` |
| `?search=mot` | **Recherche textuelle** | `title`, `description` | `?search=suite` |
| `?ordering=champ` | **Tri** | `id`, `created_at`, `modified_at`, `difficulty`, `type`, `grade_level` | `?ordering=-difficulty` |

> *Le tri par défaut est sur `id` (ascendant).*

### ⚡ Actions disponibles (Payload API)
Pour faciliter le travail du frontend (ex: afficher ou masquer un bouton Éditer et un bouton Supprimer), chaque nœud renvoyé par l'API contient maintenant un champ `actions` calculé dynamiquement pour l'utilisateur courant :
```json
"actions": {
    "edit": true,
    "delete": true
}
```
* **`edit`** : L'utilisateur a le droit de modifier le nœud (PUT/PATCH).
* **`delete`** : L'utilisateur a le droit de supprimer le nœud (DELETE).
Pour l'instant edit et delete sont toujours égales. (Même permission)
---

## 2. Modèle `NodeLink` (Relations Parent -> Enfant)
**Endpoint :** `GET /api/nodelinks/`

*Permet de structurer le cours (ex: lier une Leçon à un Chapitre).*

### 🔒 Permissions
* **Lecture (GET)** : Hérite des droits du nœud `parent`. Si l'utilisateur peut voir le parent, il peut voir ses liens.
* **Création (POST)** : 
  > [!IMPORTANT]
  > Le payload JSON **doit** contenir la clé `"parent"`. 
  Seul le propriétaire (`owner`) du nœud `parent` (ou un admin) a le droit de lui ajouter des enfants.
* **Modification / Suppression (PUT, PATCH, DELETE)** : Seul le propriétaire du nœud `parent` (ou un admin) peut modifier/détruire la structure.

### 🔍 Paramètres d'URL disponibles

| Paramètre | Fonctionnalité | Champs supportés | Exemple |
|---|---|---|---|
| `?champ=valeur` | **Filtrage exact** | `parent`, `child` | `?parent=5` |
| `?ordering=champ` | **Tri** | `id`, `order_index` | `?ordering=order_index` |

> *Le tri par défaut est sur `order_index` (ascendant).*

---

## 3. Modèle `ClassGroupSyllabus` (Liaisons Syllabus -> Groupe)
**Endpoint principal :** `/api/classgroupsyllabus/`

*Permet d'assigner un programme (Syllabus) entier à une classe d'élèves.*

### 🔒 Permissions
* **Lecture (GET)** : Accessible à tous les membres (élèves et professeurs) du groupe de classe concerné (ou un admin).
* **Création, Modification, Suppression (POST, PUT, DELETE)** : Réservée aux **administrateurs du groupe de classe** ou aux admins du site.

### 🔍 Paramètres d'URL disponibles

| Paramètre | Fonctionnalité | Champs supportés | Exemple |
|---|---|---|---|
| `?champ=valeur` | **Filtrage exact** | `class_group`, `node` | `?class_group=3` |
| `?ordering=champ` | **Tri** | `id`, `order_index` | `?ordering=-id` |

> *Le tri par défaut est sur `order_index` (ascendant).*

