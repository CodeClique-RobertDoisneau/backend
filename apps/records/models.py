from django.db import models


class Attempt(models.Model):
    """ Un essai / une réponse d'un utilisateur à un quiz ou un exercice.
    Chaque enregistrement a vocation à ne jamais être modifié. """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=False)
    node = models.ForeignKey('courses.Node', on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now_add=True, null=False)
    attempt = models.JSONField(null=False)

    def __str__(self):
        return f"Attempt : {self.user} {self.node} {self.date}"
