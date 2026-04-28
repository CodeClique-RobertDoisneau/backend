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
    public = BooleanField(null=False, default=False)
    title = CharField(max_length=150, blank=False, null=False)
    description = TextField(blank=True, null=False)
    grade_level = CharField(max_length=2, choices=GradeLevel.choices, blank=True, null=False)
    difficulty = IntegerField(choices=Difficulty.choices, blank=True, null=True)
    subject = CharField(max_length=2, choices=Subject.choices, blank=True, null=False)
    content = JSONField(blank=True, null=False)
    authorized_groups = models.ManyToManyField('users.ClassGroup', related_name='authorized_nodes', blank=True)

    children = ManyToManyField('self', through='NodeLink', symmetrical=False, related_name='parents',
                               through_fields=('parent', 'child'))

    def __str__(self):
        node_type = self.get_type_display()
        subject = self.get_subject_display()
        grade = self.get_grade_level_display()

        return f"Node : {self.title} ({node_type}, {subject}, {grade})"

    def update_authorized_groups(self, visited=None):
        """
        Met à jour les authorized_groups qui doivent être les authorized_groups hérités des parents
        + les ClassGroups explicitement liés (via class_groups) dans le cas d'un syllabus.
        Propage les changements aux enfants.
        """
        if visited is None:
            visited = set()
        
        # On prévient d'une boucle infinie en cas de cyle dans le graphe des noeuds
        if self.pk in visited:
            return
        visited.add(self.pk)

        expected_groups = set(self.class_groups.all())
        for parent in self.parents.all():
            expected_groups.update(parent.authorized_groups.all())
        
        current_groups = set(self.authorized_groups.all())
        
        if expected_groups != current_groups:
            self.authorized_groups.set(expected_groups)
            for child in self.children.all():
                child.update_authorized_groups(visited)


class NodeLink(models.Model):

    parent = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='child_links')
    child = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='parent_links')
    order_index = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('parent', 'child')

    def __str__(self):
        return f"NodeLink : {self.parent} -> {self.child}"


class ClassGroupSyllabus(models.Model):

    class_group = models.ForeignKey('users.ClassGroup', on_delete=models.CASCADE, related_name='syllabus_links')
    node = models.ForeignKey('Node', on_delete=models.CASCADE, related_name='class_group_links')
    order_index = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('class_group', 'node')

    def __str__(self):
        return f"CourseGroupSyllabus : {self.class_group} -- {self.node}"