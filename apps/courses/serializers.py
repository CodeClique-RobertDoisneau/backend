from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.courses.models import Node
import copy


class NodeSerializer(ModelSerializer):
    content = SerializerMethodField()

    class Meta:
        model = Node
        fields = ['owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content']

    def get_content(self, obj):
        if obj.type == Node.Type.QUIZ:
            content = copy.deepcopy(obj.content)
            for question in content["quiz"]:
                try:
                    question.pop("answers")
                except KeyError:
                    continue
            return content
        else :
            return obj.content


class NodeAnswersSerializer(ModelSerializer):

    class Meta:
        model = Node
        fields = ['owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content']
