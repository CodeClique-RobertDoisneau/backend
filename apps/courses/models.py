from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db.models import ManyToManyField, JSONField
from django.db.models.fields import CharField, TextField, DateTimeField, IntegerField, BooleanField


class Node(models.Model):

    class Type(models.TextChoices):
        SYLLABUS = "SY", _("Programme")
        CHAPTER = "CH", _("Chapitre")
        SECTION = "SE", _("Partie")
        LESSON = "LE", _("Leçon")
        QUIZ = "QU", _("Quiz")
        EXERCISE = "EX", _("Exercice")

    class GradeLevel(models.TextChoices):
        SECONDE = 'SE', _("Seconde")
        PREMIERE = 'PR', _("Première")
        TERMINALE = 'TE', _("Terminale")

    class Difficulty(models.IntegerChoices):
        EASY = 1, _("Facile")
        MEDIUM = 2, _("Moyen")
        HARD = 3, _("Difficile")

    class Subject(models.TextChoices):
        MATHS = "MA", _("Mathématiques")
        PHYSICS = "PH", _("Physique")
        COMPUTER_SCIENCE = "CO", _("Numérique et sciences informatiques")

    owner = models.ForeignKey('users.User', on_delete=models.SET_NULL, blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    modified_at = DateTimeField(auto_now=True)
    type = CharField(max_length=2, choices=Type.choices,  blank=False, null=False)
    public = BooleanField(null=False)
    title = CharField(max_length=150, blank=False, null=False)
    description = TextField(blank=True, null=False)
    grade_level = CharField(max_length=2, choices=GradeLevel.choices)
    difficulty = IntegerField(choices=Difficulty.choices, blank=False, null=False)
    subject = CharField(max_length=2, choices=Subject.choices, blank=False, null=False)
    content = JSONField(blank=False, null=False)

    children = ManyToManyField('self', through='NodeNode', symmetrical=False, related_name='parents',
                               through_fields=('parent', 'child'))

    def __str__(self):
        node_type = self.get_type_display()
        subject = self.get_subject_display()
        grade = self.get_grade_level_display()

        return f"Node : {self.title} ({node_type}, {subject}, {grade})"

class NodeNode(models.Model):

    parent = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='child_links')
    child = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='parent_links')
    order_index = models.IntegerField(null=False)

    class Meta:
        unique_together = ('parent', 'child')

    def __str__(self):
        return f"NodeNode : {self.parent} -> {self.child}"


class ClassGroupSyllabus(models.Model):

    class_group = models.ForeignKey('users.ClassGroup', on_delete=models.CASCADE)
    node = models.ForeignKey('Node', on_delete=models.CASCADE)
    order_index = models.IntegerField(null=False)

    class Meta:
        unique_together = ('class_group', 'node')

    def __str__(self):
        return f"CourseGroupSyllabus : {self.class_group} -- {self.node}"