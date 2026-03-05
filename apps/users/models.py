from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    class Role(models.TextChoices):
        STUDENT = "ST", _("Elève")
        TEACHER = "TE", _("Professeur")
        ADMIN = "AD", _("Administrateur")

    role = models.CharField(max_length=2, choices=Role.choices, blank=False, null=False)



class ClassGroup(models.Model):
    class_name = models.CharField(max_length=50, blank=False, null=False)
    academic_year = models.CharField(max_length=50, blank=False, null=False)
    users = models.ManyToManyField(User, through='Membership', related_name="class_groups")
    join_code = models.CharField(max_length=6, blank=True, null=False)

    def __str__(self):
        return self.class_name


class Membership(models.Model):
    """ Table intermédiaire de la relation plusieurs à plusieurs ClassGroup - Group """

    class Status(models.TextChoices):
        MEMBER = "ME", _("Membre")
        ADMIN = "AD", _("Administrateur")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.CASCADE)
    user_status = models.CharField(max_length=2, choices=Status.choices)

    class Meta:
        unique_together = ('user', 'class_group')


