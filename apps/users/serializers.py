from rest_framework.serializers import ModelSerializer

from apps.users.models import User, ClassGroup


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']

class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'groups', 'class_groups']


class ClassGroupSerializer(ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = '__all__'
