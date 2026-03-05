from rest_framework.serializers import HyperlinkedModelSerializer

from apps.users.models import User, ClassGroup

class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'first_name', 'last_name', 'email', 'groups', 'class_groups']


class ClassGroupSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ClassGroup
        fields = ['url', 'id', 'class_name', 'academic_year', 'users', 'syllabus', 'join_code']
