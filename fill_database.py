from courses.models import GradeLevel, Chapter, Section, Item, ItemType

''' Script qui permet de remplir la base de données 
avec les valeurs d'exemple données dans le readme.md.'''


chap1 = Chapter()
chap1.title = "Chapitre 1 : Variables"
chap1.description = ""
chap1.grade_level = GradeLevel.SECONDE
chap1.save()



chap2 = Chapter()
chap2.title = "Chapitre 2 : Les boucles"
chap2.description = ""
chap2.grade_level = GradeLevel.SECONDE
chap2.save()


sec1 = Section()
sec1.title = "Partie 1 : les conditions"
sec1.difficulty = 1
sec1.save()
sec1.chapters.add(chap2)



sec2 = Section()
sec2.title = "Partie 2 : les boucles - while"
sec2.difficulty = 1
sec2.save()
sec2.chapters.add(chap2)



sec3 = Section()
sec3.title = "Partie 3 : les boucles - for"
sec3.difficulty = 1
sec3.save()
sec3.chapters.add(chap2)

item1 = Item()
item1.name = "Introduction et I"
item1.item_type = ItemType.LESSON
item1.content = '''## INTRODUCTION
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
```'''
item1.difficulty = 1
item1.save()
item1.sections.add(sec1)


item2 = Item()
item2.name = "exercice d'application directe I et II"
item2.item_type = ItemType.EXAMPLE
item2.content = '''1) Crée une variable mot_de_passe. Si le mot de passe est "PythonIsCool", affiche "Accès autorisé", sinon affiche "Accès refusé".'''
item2.difficulty = 1
item2.save()
item2.sections.add(sec1)


item3 = Item()
item3.name = "III"
item3.item_type = ItemType.LESSON
item3.content = '''## III/ L'instruction "elif" (sinon si) 
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
```'''
item3.difficulty = 1
item3.save()
item3.sections.add(sec1)



item4 = Item()
item4.name = "exercice d'application directe III"
item4.item_type = ItemType.EXAMPLE
item4.content = '''2) Crée une variable x. Affiche si le nombre est positif, négatif ou nul (indice : utilise elif).'''
item4.difficulty = 1
item4.save()
item4.sections.add(sec1)




