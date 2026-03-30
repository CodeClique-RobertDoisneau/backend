from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.users.models import Membership, User


class IsGroupMember(BasePermission):
    """ Donne accès à tous les membres du groupe (membre ou admin) """

    def has_object_permission(self, request, view, obj):
        return Membership.objects.filter(user=request.user, class_group=obj).exists()

class IsGroupAdmin(BasePermission):

    def has_object_permission(self, request, view, obj):
        return Membership.objects.filter(user=request.user, class_group=obj, user_status=Membership.Status.ADMIN).exists()

class IsTeacher(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER

class IsMembershipGroupAdmin(BasePermission):
    """
    Vérifie si l'utilisateur est un administrateur du ClassGroup 
    auquel le Membership est lié.
    """
    def has_object_permission(self, request, view, obj):
        # Si c'est un administrateur global du site, on peut lui donner accès
        if request.user.is_staff or request.user.is_superuser:
            return True
        return Membership.objects.filter(
            user=request.user, 
            class_group=obj.class_group, 
            user_status=Membership.Status.ADMIN
        ).exists()