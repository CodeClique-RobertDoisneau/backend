from apps.records.serializers import AttemptSerializer
from apps.courses.serializers import NodeListSerializer
from django.utils import dateparse, timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError

from apps.courses.models import Node, NodeLink, ClassGroupSyllabus
from apps.courses.serializers import NodeDetailSerializer, NodeAnswersSerializer, NodeLinkSerializer, \
    ClassGroupSyllabusSerializer
from apps.records.models import Attempt, Progress
from apps.users.models import User
from django.db.models import Q
from apps.courses.permissions import (
    CanRetrieveNode, CanCreateNode, CanEditNode, 
    CanRetrieveNodeLink, CanEditNodeLink, 
    CanRetrieveSyllabusLink, CanEditClassGroupSyllabus
)
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.records.services import get_descendant_leaves_map, compute_simple_stats, compute_detailed_stats, compute_timeline
from collections import defaultdict


class NodeViewSet(ModelViewSet):

    serializer_class = NodeDetailSerializer
    queryset = Node.objects.all()

    # Configuration des filtres
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # 1. Filtres exacts (ex: ?type=QU&difficulty=2)
    filterset_fields = ['type', 'subject', 'grade_level', 'difficulty', 'public', 'owner']

    # 2. Recherche textuelle (ex: ?search=boucle for)
    search_fields = ['title', 'description']

    # 3. Tri (ex: ?ordering=-created_at)
    ordering_fields = ['id', 'created_at', 'modified_at', 'difficulty']
    ordering = ['id'] # Tri par défaut
        
    def get_permissions(self):
        if self.action in ["answer", "progress", "stats", "detailed_stats", "timeline"]:
            return [IsAuthenticated()]
        if self.action == "create":
            return [CanCreateNode()]
        if self.action in ["update", "partial_update", "destroy"]:
            return [CanEditNode()]
        if self.action in ["retrieve", "list"]:
            return [CanRetrieveNode()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        q_objects = Q(public=True)
        if self.request.user.is_authenticated:
            q_objects |= Q(owner=self.request.user)
            q_objects |= Q(authorized_groups__users=self.request.user)
            
        return queryset.filter(q_objects).distinct()

    @action(detail=True, methods=['GET', 'POST'], url_path='answer')
    def answer(self, request, pk):
        node = self.get_object()

        if request.method == 'GET':
            attempts = Attempt.objects.filter(user=request.user, node=node)
            serializer = AttemptSerializer(attempts, many=True, context=self.get_serializer_context())
            return Response(serializer.data, status=HTTP_200_OK)

        elif request.method == 'POST':
            if not "modified_at" in request.data or not "answer" in request.data:
                raise ValidationError("JSON invalide.")

            user_modified_at = request.data["modified_at"]
            
            if node.modified_at != dateparse.parse_datetime(user_modified_at):
                return Response(
                    {"detail": "Ce nœud a été modifié par le professeur pendant que vous répondiez. Veuillez rafraîchir la page."}, 
                    status=HTTP_409_CONFLICT
                )
            
            user_answer = request.data["answer"]
            if node.type == Node.Type.QUIZ:
                correct_answers = [q.get("answers") for q in node.content]

                # On vérifie que les réponses de l'utilisateur sont sous le bon format
                if len(user_answer) != len(correct_answers):
                    raise ValidationError("JSON invalide.")
                for q_a, q_b in zip(user_answer, correct_answers):
                    if not isinstance(q_a, list) or len(q_a) != len(q_b):
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
                correct_answer = node.content.get("answer")

                # On vérifie que la réponse de l'utilisateur est au bon format
                if not isinstance(user_answer, str):
                    raise ValidationError("JSON invalide.")

                serializer = NodeAnswersSerializer(node)


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
                raise ValidationError("Le type de noeud est invalide.")

    @action(detail=True, methods=['POST'], url_path='progress')
    def progress(self, request, pk):
        node = self.get_object()

        if not "action_performed" in request.data or \
            request.data["action_performed"] not in ["opened", "studied", "completed"]:
            raise ValidationError("JSON invalide")
        
        action_performed = request.data["action_performed"]
        progress, created = Progress.objects.get_or_create(user=request.user, node=node)

        if action_performed == "studied" and progress.status == Progress.Status.NOT_STARTED:
            progress.in_progress_at = timezone.now()
            progress.status = Progress.Status.IN_PROGRESS
        
        if action_performed == "completed" and progress.status != Progress.Status.COMPLETED:
            progress.status = Progress.Status.COMPLETED
            progress.completed_at = timezone.now()

        progress.save()

        return Response(status=HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='stats')
    def stats(self, request, pk=None):
        node = self.get_object()
        
        # On récupère toutes les feuilles de ce noeud (Leçons, Quiz, Exercices)
        leaves_map = get_descendant_leaves_map([node])
        leaves = leaves_map.get(node.id, [])
        
        # On récupère les progressions de l'utilisateur pour ne faire qu'une seule requête
        leaf_ids = [leaf.id for leaf in leaves]
        progresses = Progress.objects.filter(user=request.user, node_id__in=leaf_ids)
        progresses_by_node_id = {p.node_id: p for p in progresses}
        
        stats = compute_simple_stats(leaves, progresses_by_node_id)
        return Response(stats, status=HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='detailed-stats')
    def detailed_stats(self, request, pk=None):
        node = self.get_object()
        
        leaves_map = get_descendant_leaves_map([node])
        leaves = leaves_map.get(node.id, [])
        
        leaf_ids = [leaf.id for leaf in leaves]
        progresses = Progress.objects.filter(user=request.user, node_id__in=leaf_ids)
        progresses_by_node_id = {p.node_id: p for p in progresses}
        
        detailed_stats = compute_detailed_stats(leaves, progresses_by_node_id)
        return Response(detailed_stats, status=HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='timeline')
    def timeline(self, request, pk=None):
        node = self.get_object()
        
        leaves_map = get_descendant_leaves_map([node])
        leaves = leaves_map.get(node.id, [])
        
        leaf_ids = [leaf.id for leaf in leaves]
        progresses = Progress.objects.filter(user=request.user, node_id__in=leaf_ids)
        progresses_by_node_id = {p.node_id: p for p in progresses}
        
        attempts = Attempt.objects.filter(user=request.user, node_id__in=leaf_ids)
        attempts_by_node_id = defaultdict(list)
        for att in attempts:
            attempts_by_node_id[att.node_id].append(att)
            
        timeline_data = compute_timeline(progresses_by_node_id, attempts_by_node_id)
        return Response(timeline_data, status=HTTP_200_OK)

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

        serializer = NodeListSerializer(nodes, many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class NodeLinkViewSet(ModelViewSet):
    queryset = NodeLink.objects.all()
    serializer_class = NodeLinkSerializer

    # Configuration des filtres
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # 1. Filtres exacts (ex: GET /api/nodelinks/?parent=2)
    filterset_fields = ['parent', 'child']

    # 2. Tri (ex: ?ordering=-id)
    ordering_fields = ['id', 'order_index']
    ordering = ['order_index'] # Tri par défaut
    

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanEditNodeLink()]
        if self.action in ["retrieve", "list"]:
            return [CanRetrieveNodeLink()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
            
        q_objects = Q(parent__public=True)
        if self.request.user.is_authenticated:
            q_objects |= Q(parent__owner=self.request.user)
            q_objects |= Q(parent__authorized_groups__users=self.request.user)
            
        return queryset.filter(q_objects).distinct()

class ClassGroupSyllabusViewSet(ModelViewSet):
    queryset = ClassGroupSyllabus.objects.all()
    serializer_class = ClassGroupSyllabusSerializer

    # Configuration des filtres
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # 1. Filtres exacts (ex: GET /api/classgroupsyllabus/?class_group=3)
    filterset_fields = ['class_group', 'node']

    # 2. Tri (ex: ?ordering=-id)
    ordering_fields = ['id', 'order_index']
    ordering = ['order_index'] # Tri par défaut

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [CanEditClassGroupSyllabus()]
        if self.action in ["retrieve", "list"]:
            return [CanRetrieveSyllabusLink()]
        return super().get_permissions()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
            
        if self.request.user.is_authenticated:
            return queryset.filter(class_group__users=self.request.user).distinct()
        return queryset.none()









