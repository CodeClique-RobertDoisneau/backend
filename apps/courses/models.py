from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ManyToManyField
from django.db.models.fields import CharField, TextField, DateTimeField, IntegerField


class GradeLevel(models.TextChoices):
    SECONDE = 'SECONDE'
    PREMIERE = 'PREMIERE'
    TERMINALE = 'TERMINALE'

class ItemType(models.TextChoices):
    LESSON = 'LESSON'
    EXERCICE = 'EXERCICE'
    QUIZZ = 'QUIZZ'


class Chapter(models.Model):

    title = CharField(max_length=100)
    description = TextField(blank=True)
    grade_level = CharField(choices=GradeLevel.choices, max_length=9)

    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)


    def __str__(self):
        return f'{self.title}'

class Section(models.Model):

    title = CharField(max_length=100)
    description = TextField(blank=True)
    difficulty = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    chapters = ManyToManyField(Chapter, related_name='sections')

    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'

class Item(models.Model):

    title = CharField(max_length=100)
    item_type = CharField(choices=ItemType.choices, max_length=8)
    content = TextField(null=True, blank=True) # Contenu en markdown de l'item
    difficulty = IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    sections = ManyToManyField(Section, related_name='items')

    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.title}'
