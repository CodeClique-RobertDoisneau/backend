# Documentation Backend pour le Frontend

Toutes les étapes sont nécessaires afin que le backend fonctionne correctement sur votre ordinateur.

## Importer le backend depuis github
Aller dans votre dossier projet (le dossier qui contient les dossiers backend et frontend), puis mettez à jour les
fichiers à l'aide de \
`git pull` \
Ensuite, vous devez mettre à jour les fichiers dans le dossier backend :  \
`git switch dev` \
`git pull`

## Initialiser la base de données
Le code backend (qui se trouve dans backend/) est indépendant de la base de données postgresql (qui se trouve dans un 
volume nommé "codeclique_postgres_data" de docker).
Une fois que vous avez importé la dernière version du backend, la base de données (bdd) ne s'est pas automatiquement mise à jour pour correspondre au code backend.
Il faut donc la mettre à jour en éxécutant la commande suivante après avoir lancé docker (`docker compose up --build`): \
`docker compose exec backend python manage.py migrate` \
(pour exécuter une commande avec le conteneur docker lancé, il suffit d'ouvrir un autre terminal dans le même dossier) \
S'il y a des conflits dans les migrations (=mises à jour de la base de données), n'hésitez pas à vider de la base de 
données (seulement votre version locale sera vidée) en supprimant le volume codeclique_postgres_data (avec la commande
`docker volume remove codeclique_postgres_data` ou `docker compose down -v`). Ensuite réexécuter la commande ci-dessus.

## Remplir la base de données
Quand vous lancez pour la première fois le site avec Docker, et donc le backend, la base de données est vide. Afin que les endpoints ci-dessus ne renvoient pas des listes et des JSON vides, il est préférable pour le développement du frontend d'ajouter du contenu dans la base de données. Pour cela, deux options : 
1. Lancer la commande suivante : \
`docker compose exec -T backend python manage.py shell < backend/fill_database.py` \
Le script fill_database.py va faire le travail.

2. Utiliser l'administration Django pour apprendre à manipuler la bdd :
 
   1) Lancez votre serveur docker
   `docker compose up` ou `docker compose up --build` si vous venez d'importer le backend

   2) Créez-vous un superuser avec la commande suivante
   `docker compose exec backend python manage.py createsuperuser`
   Renseignez alors un identifiant et un mot de passe, l'adresse mail est facultative (taper juste [Entrer]) (tout est en local, vous pouvez mettre n'importe quoi).

   3) Accéder à l'admin Django via l'url suivant : 
   `localhost/api/admin/`
   Il devrait alors s'afficher l'interface suivante : 
   ![admin_authentification_screenshot.png](doc/admin_authentification_screenshot.png)
   Puis, après avoir entré les identifiants que vous venez de créer, vous devriez avoir l'interface suivante : 
   ![admin_home_screenshot.png](doc/admin_home_screenshot.png)


L'interface est normalement très intuitif, vous pouvez maintenant ajouter, modifier et supprimer autant de modèles (=tuples de la bdd) que vous voulez dans la base de données !
Afin de faire vos tests pour le frontend, vous pouvez par exemple ajouter les modèles suivants dans la base de données : 

- 2 chapitres : 
  - title : `Chapitre 1 : Variables` \
  description : ce que vous voulez \
  grade_level : `Seconde`
  - title : `Chapitre 2 : Les boucles` \
  description : ce que vous voulez \
  grade_level : `Seconde`


- 3 sections dans le chapitre 2 :
  - title : `Partie 1 : les conditions` \
  difficulty : `1` \
  chapters : Chapitre 2 : Les boucles (il faut le sélectionner)

  - title : `Partie 2 : les boucles - while` \
  difficulty : `1` \
  chapters : Chapitre 2 : Les boucles (il faut le sélectionner)

  - title : `Partie 3 : les boucles - for` \
  difficulty : `1` \
  chapters : Chapitre 2 : Les boucles (il faut le sélectionner)


- 4 items dans la section Partie 1 : les conditions :
  - name : `Introduction et I` \
  content : 
    ````markdown
    ## INTRODUCTION
    Jusqu'à présent, nos programmes étaient linéaires : ils exécutaient les instructions les unes après les autres, toujours de la même façon. Mais dans la vie, on fait des choix ! "S'il pleut, je prends un parapluie, sinon je mets des lunettes de soleil". En Python, c'est pareil : on utilise des "conditions" pour dire à l'ordinateur d'exécuter certaines lignes de code seulement si une condition est remplie.
    
    ## I/ L'instruction "if" (si) 
    C'est la base de la condition. On teste si quelque chose est Vrai (True).
    
    **Syntaxe :** 
    ```python
    if condition : 
        # Instruction à exécuter si c'est vrai
    ```
    
    **⚠️ Attention !**   
    Ne pas oublier les deux points ":" à la fin de la ligne du if.  
    L'indentation (le décalage vers la droite) est obligatoire ! C'est elle qui dit à Python : "cette ligne fait partie du bloc conditionnel".
    
    **Exemple :** 
    ```python
    age = 18 
    if age >= 18: 
        print("Vous êtes majeur !")
    ```
    
    ## II/ L'instruction "else" (sinon) 
    C'est l'alternative. Si la condition du if est fausse, alors on exécute ce qu'il y a dans le else.
    
    **Syntaxe :** 
    ```python
    if condition : 
        # Fait ça si c'est vrai 
    else : 
        # Fait ça si c'est faux
    ```
    
    **Exemple :** 
    ```python
    note = 8 
    if note >= 10: 
        print("Bravo, tu as la moyenne !") 
    else: 
        print("Il faut encore réviser un peu.")
    ```
    ````
    difficulty : `1` \
    sections : Partie 1 : les conditions (il faut le sélectionner)
    
  - name : exercice d'application directe I et II \
    content : 
    ````markdown
    1) Crée une variable mot_de_passe. Si le mot de passe est "PythonIsCool", affiche "Accès autorisé", sinon affiche "Accès refusé".
    ````
    difficulty : `1` \
    sections : Partie 1 : les conditions (il faut le sélectionner)

  - name : `III` \
  content : 
    ````markdown
    ## III/ L'instruction "elif" (sinon si) 
    Parfois, le monde n'est pas tout blanc ou tout noir, il y a plusieurs cas possibles. elif (contraction de "else if") permet de tester une nouvelle condition si la première est fausse.
    
    **Exemple :**
    ```python
    temperature = 20
    
    if temperature > 30: 
        print("Il fait très chaud !") 
    elif temperature > 15: 
        print("Il fait bon.") 
    else: 
        print("Il fait froid, mets un manteau !")
    ```
    ````
    difficulty : `1` \
    sections : Partie 1 : les conditions (il faut le sélectionner)

  - name : `exercice d'application directe III` \
  content : 
    ````markdown
    2) Crée une variable x. Affiche si le nombre est positif, négatif ou nul (indice : utilise elif).
    ````
    difficulty : `1` \
    sections : Partie 1 : les conditions (il faut le sélectionner)


## Remarques 
- L'attribut `name` de Item n'est jamais affiché dans le frontend. Il sert juste à mieux repérer les différents items lorsque que nous gérons la base de données.
- Les exercices d'application directe sont les "exemple de cours" intéractifs où les profs pourront afficher un code au tableau et permettre à tous les élèves de s'éxercer en direct. 
- L'ItemType `Example` signifie exercice d'application directe (autrement appelé "exemple de cours")



## Endpoints utiles pour le frontend
* `/api/chapter/` : liste de tous les chapitres avec les attributs `['id', 'title', 'description', 'grade_level']` *(c'est pour la page d'accueil avec tous les chapitres)*
* `/api/chapter/{id}` : détail d'un chapitre (`['id', 'title', 'description', 'grade_level', 'created_at', 'modified_at', 'sections']`) où `sections` est une liste des sections du chapitre avec les attributs `['id', 'title', 'description', 'difficulty']` *(c'est pour la page d'un chapitre avec toutes les sections (=notions))*
* `/api/section/{id}` : détail d'une section (`['id', 'title', 'description', 'difficulty', 'created_at', 'modified_at', 'items']`) où `items` est une liste des items de la section avec les attributs `['id', 'title', 'item_type', 'difficulty']` *(c'est pour afficher la page d'une section (=notion))*
* `/api/item/{id}` : détail d'un item en particulier `['id', 'title', 'item_type', 'content', 'difficulty', 'created_at', 'modified_at']` *(c'est pour la page avec seulement un item, par exemple quand le prof veut faire faire un exemple à tous les élèves)*
