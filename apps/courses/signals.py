from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.courses.models import NodeLink, ClassGroupSyllabus, Node

@receiver([post_save, post_delete], sender=NodeLink)
def update_node_groups_on_link_change(sender, instance, **kwargs):
    # En post_delete, on s'assure que l'enfant existe toujours en base 
    # (pour éviter un plantage si l'enfant a été supprimé et a déclenché un CASCADE)
    if instance.child_id and Node.objects.filter(id=instance.child_id).exists():
        instance.child.update_authorized_groups()

@receiver([post_save, post_delete], sender=ClassGroupSyllabus)
def update_node_groups_on_syllabus_change(sender, instance, **kwargs):
    if instance.node_id and Node.objects.filter(id=instance.node_id).exists():
        instance.node.update_authorized_groups()