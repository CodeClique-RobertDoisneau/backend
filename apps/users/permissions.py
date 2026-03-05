from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.users.models import Membership, User


class IsGroupMember(BasePermission):
    """ Donne accès en read only à tous les membres du groupe et donne accès en write aux admins du groupe """

    def has_object_permission(self, request, view, obj):

        membership = Membership.objects.filter(user=request.user, class_group=obj).first()
        if not membership:
            return False
        elif request.method in SAFE_METHODS: # Read
            return True
        else: # Write
            return membership.user_status == Membership.Status.ADMIN

class IsTeacher(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == User.Role.TEACHER