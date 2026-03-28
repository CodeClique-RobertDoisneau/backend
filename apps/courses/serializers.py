from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.courses.models import Node
import copy

class NodeSerializer(ModelSerializer):

    class Meta:
        model = Node
        fields = ['owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content']

    def to_representation(self, instance):
        
        response = super().to_representation(instance)

        content = copy.deepcopy(response.get("content", {}))

        if instance.type == Node.Type.QUIZ:
            for question in content.get("quiz", []):
                question.pop("answers", None)
        elif instance.type == Node.Type.EXERCISE:
            content.get("ex", {}).pop("answer", None)
        
        response["content"] = content
        return response

class NodeAnswersSerializer(ModelSerializer):

    class Meta:
        model = Node
        fields = ['owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content']
