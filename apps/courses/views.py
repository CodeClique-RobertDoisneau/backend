from django.utils import dateparse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.exceptions import ValidationError

from apps.courses.models import Node, NodeNode, ClassGroupSyllabus
from apps.courses.serializers import NodeDetailSerializer, NodeAnswersSerializer, NodeNodeSerializer, \
    ClassGroupSyllabusSerializer
from apps.records.models import Attempt
from apps.users.models import User


class NodeViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):

    serializer_class = NodeDetailSerializer
    queryset = Node.objects.all()

    def get_permissions(self):
        if self.action == "answer":
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['POST'], url_path='answer')
    def answer(self, request, pk):
        if not "modified_at" in request.data or not "answer" in request.data:
            raise ValidationError("JSON invalide.")

        user_modified_at = request.data["modified_at"]
        node = self.get_object()

        if node.modified_at != dateparse.parse_datetime(user_modified_at):
            return Response(
                {"detail": "Ce nœud a été modifié par le professeur pendant que vous répondiez. Veuillez rafraîchir la page."}, 
                status=HTTP_409_CONFLICT
            )
        
        user_answer = request.data["answer"]
        if node.type == Node.Type.QUIZ:
            quiz_data = node.content.get("data", []) if isinstance(node.content, dict) else node.content
            correct_answers = [q.get("answers") for q in quiz_data if isinstance(q, dict)]

            # On vérifie que les réponses de l'utilisateur sont sous le bon format
            if len(user_answer) != len(correct_answers):
                print("Différente taille.")
                raise ValidationError("JSON invalide.")
            for q_a, q_b in zip(user_answer, correct_answers):
                if not isinstance(q_a, list) or len(q_a) != len(q_b):
                    print("Pas de sous-liste ou différente taille de sous-liste.")
                    raise ValidationError("JSON invalide.")

                for a in q_a: 
                    if not isinstance(a, bool):
                        raise ValidationError("JSON invalide.")       


            # On enregistre les données de l'essai dans la base de données
            serializer = NodeAnswersSerializer(node)
            Attempt.objects.create(
                user=request.user,
                node=node,
                attempt={
                    "node": serializer.data, # On enregiste le JSON du noeud pour le cas où le noeud est modifié à l'avenir.
                    "answer": user_answer
                }
            )

            return Response({"content": {"data": node.content.get("data", [])}}, status=HTTP_200_OK)

        elif node.type == Node.Type.EXERCISE:
            correct_answer = node.content.get("answer")

            # On vérifie que la réponse de l'utilisateur est au bon format
            if not isinstance(user_answer, str):
                raise ValidationError("JSON invalide.")

            serializer = NodeAnswersSerializer(self.get_object())


            Attempt.objects.create(
                user=request.user, 
                node=node, 
                attempt={
                    "node": serializer.data, 
                    "answer": user_answer
                }
            )

            return Response({ "correct" : user_answer == correct_answer },
                            status=HTTP_200_OK)
        
        elif node.type == Node.Type.LESSON:
            serializer = NodeAnswersSerializer(node)
            Attempt.objects.create(
                user=request.user, 
                node=node, 
                attempt={
                    "node": serializer.data, 
                    "answer": user_answer
                }
            )
            return Response(status=HTTP_200_OK)

        else:
            raise ValidationError("Le type de nœud est invalide.")

    @action(detail=False, methods=['GET'], url_path=r'codeclique(?:/(?P<path>[a-z/]+))?')
    def codeclique(self, request, path=None):
        try:
            codeclique_user = User.objects.get(username="codeclique")
        except User.DoesNotExist:
            return Response(status=HTTP_500_INTERNAL_SERVER_ERROR)
            
        nodes = Node.objects.filter(owner=codeclique_user, type=Node.Type.SYLLABUS)

        if path:
            path = path.strip('/')
            parts = path.split('/')
            
            GRADE_MAP = {
                'seconde': Node.GradeLevel.SECONDE,
                'premiere': Node.GradeLevel.PREMIERE,
                'terminale': Node.GradeLevel.TERMINALE,
            }
            SUBJECT_MAP = {
                'maths': Node.Subject.MATHS,
                'physique': Node.Subject.PHYSICS,
                'nsi': Node.Subject.COMPUTER_SCIENCE,
            }

            for part in parts:
                part_lower = part.lower()
                if part_lower in GRADE_MAP:
                    nodes = nodes.filter(grade_level=GRADE_MAP[part_lower])
                elif part_lower in SUBJECT_MAP:
                    nodes = nodes.filter(subject=SUBJECT_MAP[part_lower])
                else:
                    raise ValidationError(f"Paramètre invalide : {part}")

        serializer = NodeDetailSerializer(nodes, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class NodeNodeViewSet(ModelViewSet):
    queryset = NodeNode.objects.all()
    serializer_class = NodeNodeSerializer
    # Permet au front de faire : GET /api/nodenodes/?parent=2
    filterset_fields = ['parent', 'child']

class ClassGroupSyllabusViewSet(ModelViewSet):
    queryset = ClassGroupSyllabus.objects.all()
    serializer_class = ClassGroupSyllabusSerializer
    # Permet au front de faire : GET /api/classgroupsyllabus/?class_group=3
    filterset_fields = ['class_group', 'node']











