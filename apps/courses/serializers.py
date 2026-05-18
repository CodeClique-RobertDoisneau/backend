from rest_framework.serializers import ModelSerializer, SerializerMethodField

from apps.courses.models import Node, NodeLink, ClassGroupSyllabus
from apps.users.models import User
from apps.records.models import Progress
import copy



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

        # Ajout des actions possibles sur ce noeud pour le frontend
        request = self.context.get('request')
        user = request.user if request else None
        
        can_edit = False
        if user and user.is_authenticated:
            if user.is_staff or user.is_superuser or getattr(instance, 'owner', None) == user:
                can_edit = True
        can_get_correction = False 
        if user and user.is_authenticated:
            try:
                # On utilise .get() car l'objet est unique pour un (user, node) donné
                progress = Progress.objects.get(user=user, node=instance)
                response['progress'] = {
                    'started_at': progress.started_at.isoformat() if progress.started_at else None,
                    'in_progress_at': progress.in_progress_at.isoformat() if progress.in_progress_at else None,
                    'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                    'last_seen_at': progress.last_seen_at.isoformat() if progress.last_seen_at else None,
                    'status': progress.status
                }
                
                # Si le noeud est terminé, l'utilisateur a accès à la correction
                if progress.status == Progress.Status.COMPLETED:
                    can_get_correction = True
                    
            except Progress.DoesNotExist:
                # Valeurs par défaut si le noeud n'a jamais été ouvert par l'étudiant
                response['progress'] = {
                    'started_at': None,
                    'in_progress_at': None,
                    'completed_at': None,
                    'last_seen_at': None,
                    'status': Progress.Status.NOT_STARTED
                }
                
            # Autres conditions pour avoir la correction (professeur, admin, owner...)
            if user.is_staff or user.is_superuser or getattr(instance, 'owner', None) == user or \
                user.role == User.Role.TEACHER:
                can_get_correction = True
        else:
            response['progress'] = None

        response['actions'] = {
            'edit': can_edit,
            'delete': can_edit, 
            'get_correction' : can_get_correction
        }

        content = copy.deepcopy(response.get("content", {}))

        if not can_get_correction:
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
    # Serializer qui comprend aussi toutes les réponses aux quiz et aux exercices
    # Sert à sauvegarder l'état d'un exercice et ou d'un quiz (donc avec les réponses) pour Attempt
    # (voir apps/courses/views.py)
    # Il n'y a pas de champ children car il sert pour les exercices et les quiz. 
    class Meta:
        model = Node
        fields = ['id', 'owner', 'created_at', 'modified_at', 'type', 'public', 'title', 'description', 'grade_level',
                  'difficulty', 'subject', 'content']


class ClassGroupSyllabusSerializer(ModelSerializer):

    class Meta:
        model = ClassGroupSyllabus
        fields = ['id', 'class_group', 'node', 'order_index']