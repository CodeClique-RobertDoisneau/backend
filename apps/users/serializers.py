from rest_framework.serializers import HyperlinkedModelSerializer

from apps.courses.serializers import ClassGroupSyllabusSerializer
from apps.users.models import User, ClassGroup, Membership


class MembershipSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Membership
        fields = ['url', 'id', 'user', 'class_group', 'user_status']


class UserSerializer(HyperlinkedModelSerializer):
    class_groups = MembershipSerializer(source="class_group_links", many=True, read_only=True)

    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'first_name', 'last_name', 'email', 'groups', 'class_groups']


class ClassGroupSerializer(HyperlinkedModelSerializer):
    syllabus = ClassGroupSyllabusSerializer(source="syllabus_links", many=True, read_only=True)
    users = MembershipSerializer(source="user_links", many=True, read_only=True)
    class Meta:
        model = ClassGroup
        fields = ['url', 'id', 'class_name', 'academic_year', 'users', 'syllabus', 'join_code']
