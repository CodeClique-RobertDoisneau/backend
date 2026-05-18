from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from collections import defaultdict

from apps.records.models import Progress, Attempt
from apps.courses.models import Node, NodeLink
from apps.records.serializers import ProgressSerializer
from apps.records.services import get_descendant_leaves_map, compute_detailed_stats, compute_timeline

class ProgressViewSet(ModelViewSet):
    """
    ViewSet pour gérer la progression des utilisateurs.
    """
    queryset = Progress.objects.all()
    serializer_class = ProgressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset
        
        # Je n'ai pas encore implémenté le fait qu'un professeur peut voir la progression de 
        # ses élèves, ou l'administrateur d'un groupe sur les membres et les cours du groupe...

        # Un étudiant ne peut voir que sa propre progression
        return queryset.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['GET'], url_path='dashboard')
    def dashboard(self, request):
        user = request.user
        
        # 1. On cherche d'abord tous les programmes (Syllabus) auxquels l'étudiant a accès.
        # Soit parce qu'ils sont publics, soit il en est propriétaire, soit il est dans le groupe.
        q_objects = Q(public=True)
        q_objects |= Q(owner=user)
        q_objects |= Q(authorized_groups__users=user)
        
        accessible_syllabus = Node.objects.filter(q_objects, type=Node.Type.SYLLABUS).distinct()
        
        # 2. On récupère directement les chapitres de ces syllabus
        # Pour éviter des boucles lentes, on utilise les NodeLink
        chapters_links = NodeLink.objects.filter(
            parent__in=accessible_syllabus, 
            child__type=Node.Type.CHAPTER
        ).select_related('child')   # select_related permet de ne pas faire une seconde requête 
                                    # dans la base de données quand on fait ensuite link.child
        
        chapters = [link.child for link in chapters_links]
        
        # 3. Récupération de l'arborescence (feuilles) pour tous ces chapitres d'un seul coup
        leaves_map = get_descendant_leaves_map(chapters)
        
        # 4. Chargement complet de l'historique de l'étudiant (progressions et essais)
        # Ça semble lourd, mais en réalité filtrer sur le user est très rapide et 
        # on économise le N+1 problem.
        progresses = Progress.objects.filter(user=user)
        progresses_by_node_id = {p.node_id: p for p in progresses}
        
        attempts = Attempt.objects.filter(user=user)
        attempts_by_node_id = defaultdict(list)
        for att in attempts:
            attempts_by_node_id[att.node_id].append(att)
            
        # 5. On calcule le résumé statistique chapitre par chapitre, rangé par syllabus
        dashboard_data = {}
        for syllabus in accessible_syllabus:
            dashboard_data[syllabus.id] = {
                "title": syllabus.title,
                "chapters": []
            }
            
        # On trie les liens par order_index pour que les chapitres apparaissent dans le bon ordre
        sorted_chapter_links = sorted(chapters_links, key=lambda link: link.order_index or 0)
        
        for link in sorted_chapter_links:
            chapter = link.child
            syllabus_id = link.parent_id
            
            leaves = leaves_map.get(chapter.id, [])
            chapter_stats = compute_detailed_stats(leaves, progresses_by_node_id)
            dashboard_data[syllabus_id]["chapters"].append({
                "title": chapter.title,
                "stats": chapter_stats
            })
        
        global_timeline = compute_timeline(progresses_by_node_id, attempts_by_node_id)
        
        return Response({
            "syllabus": dashboard_data,
            "timeline": global_timeline
        })
