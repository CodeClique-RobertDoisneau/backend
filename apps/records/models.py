from django.db import models
from django.utils.translation import gettext_lazy as _


class Attempt(models.Model):
    """ Un essai / une réponse d'un utilisateur à un quiz ou un exercice.
    Chaque enregistrement a vocation à ne jamais être modifié. """
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=False, related_name='attempts')
    node = models.ForeignKey('courses.Node', on_delete=models.CASCADE, null=False, related_name='attempts')
    date = models.DateTimeField(auto_now_add=True, null=False)
    attempt = models.JSONField(null=False)
    # Format du JSON de attempt : 
    # attempt={
    #   "node": NodeAnswersSerializer.data, # On enregiste le JSON du noeud pour le cas où le noeud est modifié à l'avenir.
    #   "answer": user_answer
    # }
    # où user_answer à le format suivant
    # pour un quiz : 
    # [
    #   [true, true, false, false],
    #   [true, false, true, false]
    # ]
    # pour un exercice :
    # "42"
    # (c'est la sortie du programme python)

    def __str__(self):
        return f"Attempt : {self.user} {self.node} {self.date}"


class Progress(models.Model):
    class Status(models.TextChoices):
        NOT_STARTED = "NS", _("Non commencé")
        IN_PROGRESS = "IP", _("En cours")
        COMPLETED = "CO", _("Terminé")

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, null=False, related_name='progressions')  # 'progressions' parce que 'progress' on ne voit pas le 's'
    node = models.ForeignKey('courses.Node', on_delete=models.CASCADE, null=False, related_name='progressions')
    
    # Métriques de temps
    started_at = models.DateTimeField(auto_now_add=True, null=False)    # Date à laquelle l'utilisateur a ouvert le noeud pour la première fois
    completed_at = models.DateTimeField(null=True)                      # Date à laquelle le noeud est passé à COMPLETED, ce champ est non null ssi status = COMPLETED
    last_seen_at = models.DateTimeField(auto_now=True, null=False)      # Date de la dernière action (dernier essai ou dernière lecture)

    # État d'avancement
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.NOT_STARTED, null=False)

    class Meta:
        # Un utilisateur ne peut avoir qu'une seule progression globale par nœud
        unique_together = ('user', 'node')

    def __str__(self):
        return f"Progress : {self.user.username} - {self.node.title} : {self.get_status_display()}"
