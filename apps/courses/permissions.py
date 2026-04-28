from rest_framework.permissions import BasePermission
from apps.users.models import User, Membership
from apps.courses.models import Node


class CanRetrieveNode(BasePermission):
    """
    Permission pour lire (retrieve) un noeud :
    - L'utilisateur est admin/staff.
    - Le noeud est public (CodeClique).
    - L'utilisateur est le propriétaire (owner) du noeud.
    - L'utilisateur fait partie d'un groupe autorisé (via authorized_groups).
    """

    def has_object_permission(self, request, view, obj):
        # Accès administrateur global
        if request.user.is_staff or request.user.is_superuser:
            return True
        
        # Accès public ou si l'utilisateur est le créateur
        if getattr(obj, 'public', False) or getattr(obj, 'owner', None) == request.user:
            return True
            
        # Vérification si l'utilisateur appartient à un groupe autorisé
        if request.user.is_authenticated:
            # `users=request.user` va utiliser la relation ClassGroup -> users
            return obj.authorized_groups.filter(users=request.user).exists()
            
        return False

class CanCreateNode(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER

class CanEditNode(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        return getattr(obj, 'owner', None) == request.user

class CanRetrieveNodeLink(BasePermission):
    def has_object_permission(self, request, view, obj):
        parent = obj.parent
        if request.user.is_staff or request.user.is_superuser:
            return True
        if getattr(parent, 'public', False) or getattr(parent, 'owner', None) == request.user:
            return True
        if request.user.is_authenticated:
            return parent.authorized_groups.filter(users=request.user).exists()
        return False

class CanEditNodeLink(BasePermission):
    # On a regroupé le Create et le Edit ici car ce sont les mêmes utilisateurs qui 
    # ont la permission.
    def has_permission(self, request, view):
        # On s'occupe du create (POST)
        if request.method == 'POST':
            if request.user.is_staff or request.user.is_superuser:
                return True
            parent_id = request.data.get('parent')
            if not parent_id:
                return True # La validation du serializer s'en chargera
            try:
                parent = Node.objects.get(id=parent_id)
                return getattr(parent, 'owner', None) == request.user
            except Node.DoesNotExist:
                return False
        return True

    def has_object_permission(self, request, view, obj):
        # On s'occupe du update, partial_update et destroy (PUT, PATCH, DELETE)
        parent = obj.parent
        if request.user.is_staff or request.user.is_superuser:
            return True
        return getattr(parent, 'owner', None) == request.user

class CanRetrieveSyllabusLink(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.is_authenticated:
            # On regarde si c'est un membre/administrateur du groupe
            return Membership.objects.filter(user=request.user, class_group=obj.class_group).exists()
        return False

class CanEditClassGroupSyllabus(BasePermission):
    # De même, on a regroupé le Create et le Edit ici car ce sont les mêmes utilisateurs qui 
    # ont la permission.
    def has_permission(self, request, view):
        # On s'occupe du create (POST)
        if request.method == 'POST':
            if request.user.is_staff or request.user.is_superuser:
                return True
            class_group_id = request.data.get('class_group')
            if not class_group_id:
                return True
            if request.user.is_authenticated:
                return Membership.objects.filter(
                    user=request.user, 
                    class_group_id=class_group_id, 
                    user_status=Membership.Status.ADMIN
                ).exists()
            return False
        return True

    def has_object_permission(self, request, view, obj):
        # On s'occupe du update, partial_update et destroy (PUT, PATCH, DELETE)
        if request.user.is_staff or request.user.is_superuser:
            return True
        if request.user.is_authenticated:
            return Membership.objects.filter(
                user=request.user, 
                class_group=obj.class_group, 
                user_status=Membership.Status.ADMIN
            ).exists()
        return False