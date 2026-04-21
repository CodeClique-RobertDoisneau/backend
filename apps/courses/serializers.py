from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.courses.models import Node, NodeNode, ClassGroupSyllabus
import copy

from apps.users.models import ClassGroup


class NodeListSerializer(ModelSerializer):
    class Meta:
        model = Node
        fields = ['id', 'type', 'title', 'description', 'grade_level', 'difficulty', 'subject']


class NodeNodeChildSerializer(ModelSerializer):
    child = NodeListSerializer(read_only=True)

    class Meta:
        model = NodeNode
        fields = ['id', 'order_index', 'child']

class NodeNodeSerializer(ModelSerializer):

    class Meta:
        model = NodeNode
        fields = ['id', 'parent', 'child', 'order_index']

    
class NodeDetailSerializer(ModelSerializer):

    children = NodeNodeChildSerializer(source='child_links', many=True, read_only=True)
    user_progress = SerializerMethodField()

    class Meta:
        model = Node
        fields = ['id', 'owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content', 'children', 'user_progress']

    def get_user_progress(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        from apps.records.models import Attempt
        attempt = Attempt.objects.filter(node=obj, user=request.user).order_by('-date').first()
        if not attempt:
            return None
            
        try:
            payload = attempt.attempt
            if not isinstance(payload, dict):
                payload = {}
                
            submission = payload.get("answer")
            
            result = {
                "done": True,
                "submission": submission,
                "modified_at": attempt.date.isoformat() if attempt.date else None
            }
            
            if obj.type == Node.Type.QUIZ:
                node_data = payload.get("node", {}).get("content", {})
                quiz_data = node_data.get("data", []) if isinstance(node_data, dict) else node_data
                
                correct_answers = [q.get("answers") for q in quiz_data if isinstance(q, dict)]
                
                score = 0
                max_score = 0
                if isinstance(submission, list):
                    for q_a, q_b in zip(submission, correct_answers):
                        if isinstance(q_a, list) and isinstance(q_b, list):
                            for u_a, t_a in zip(q_a, q_b):
                                max_score += 1
                                if u_a == t_a:
                                    score += 1
                result["score"] = score
                result["max_score"] = max_score
                
            return result
        except Exception:
            return None

    def to_representation(self, instance):
        
        response = super().to_representation(instance)

        content = copy.deepcopy(response.get("content", {}))

        if instance.type == Node.Type.QUIZ:
            # Nouveau format : le tableau des questions est sous la clé "data"
            data = content.get("data", [])
            
            # Déterminer si on doit garder les réponses
            keep_answers = False
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                if request.user.role in ['AD', 'TE']:
                    keep_answers = True
                else:
                    from apps.records.models import Attempt
                    if Attempt.objects.filter(node=instance, user=request.user).exists():
                        keep_answers = True

            if not keep_answers:
                if isinstance(data, list):
                    for question in data:
                        if isinstance(question, dict):
                            question.pop("answers", None)
                            question.pop("explanation", None)
            content["data"] = data
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