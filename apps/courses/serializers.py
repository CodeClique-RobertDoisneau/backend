from rest_framework.serializers import ModelSerializer

from apps.courses.models import Node


class NodeSerializer(ModelSerializer):

    class Meta:
        model = Node
        fields = '__all__'