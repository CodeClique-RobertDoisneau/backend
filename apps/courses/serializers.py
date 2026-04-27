from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.courses.models import Node, NodeLink, ClassGroupSyllabus
import copy

from apps.users.models import ClassGroup


class NodeListSerializer(ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'type', 'title', 'description', 'grade_level', 'difficulty', 'subject']


class NodeLinkChildSerializer(ModelSerializer):
    child = NodeListSerializer(read_only=True)

    class Meta:
        model = NodeLink
        fields = ['id', 'order_index', 'child']

class NodeLinkSerializer(ModelSerializer):

    class Meta:
        model = NodeLink
        fields = ['id', 'parent', 'child', 'order_index']

    
class NodeDetailSerializer(ModelSerializer):

    children = NodeLinkChildSerializer(source='child_links', many=True, read_only=True)

    class Meta:
        model = Node
        fields = ['id', 'owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content', 'children']

    def to_representation(self, instance):
        
        response = super().to_representation(instance)

        content = copy.deepcopy(response.get("content", {}))

        if instance.type == Node.Type.QUIZ:
            if isinstance(content, list):
                for question in content:
                    if isinstance(question, dict):
                        question.pop("answers", None)
        elif instance.type == Node.Type.EXERCISE:
            if isinstance(content, dict):
                content.pop("answer", None)
        
        response["content"] = content
        return response

class NodeAnswersSerializer(ModelSerializer):

    class Meta:
        model = Node
        fields = ['id', 'owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content']


class ClassGroupSyllabusSerializer(ModelSerializer):

    class Meta:
        model = ClassGroupSyllabus
        fields = ['id', 'class_group', 'node', 'order_index']