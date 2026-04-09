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