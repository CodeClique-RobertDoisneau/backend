from django.utils import dateparse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT
from rest_framework.viewsets import GenericViewSet
from rest_framework.exceptions import ValidationError

from apps.courses.models import Node
from apps.courses.serializers import NodeSerializer, NodeAnswersSerializer
from apps.records.models import Attempt


class NodeViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):

    serializer_class = NodeSerializer
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
            correct_answers = [q.get("answers") for q in node.content["quiz"]]

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

            return Response({ "answers": correct_answers }, status=HTTP_200_OK)

        elif node.type == Node.Type.EXERCISE:
            correct_answer = node.content["ex"]["answer"]

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
        else:
            raise ValidationError("Le type de noeu est invalide.")










