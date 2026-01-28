from django.db import models
from django.db.models import FilePathField, ManyToManyField
from django.db.models.fields import CharField, EmailField, TextField, DateTimeField, IntegerField


class Chapter(models.Model):

    title = CharField(max_length=100)
    description = TextField()
    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)

class Section(models.Model):

    title = CharField(max_length=100)
    level = IntegerField()
    difficulty = IntegerField()
    chapters = ManyToManyField(Chapter, related_name='sections')


class Item(models.Model):

    title = CharField(max_length=100)
    content = TextField(null=True, blank=True) # Contenu en markdown de l'item
    level = IntegerField()
    difficulty = IntegerField()
    sections = ManyToManyField(Section, related_name='items')



