from rest_framework import permissions, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404

from apps.users.models import ClassGroup, Membership
from apps.users.serializers import ClassGroupSerializer

# ==============================================================================
# APPROCHE 1 : La méthode "DRF pur" (Celle déjà proposée, souvent recommandée)
# ==============================================================================
# Séparation totale entre la logique de permission et la logique de la vue.
# Très "propre" si tu as beaucoup de vues qui partagent les mêmes permissions.

class IsClassGroupMemberOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return Membership.objects.filter(user=request.user, class_group=obj).exists()
        if request.method in ['PUT', 'PATCH']:
            if request.user.is_superuser:
                return True
            return Membership.objects.filter(
                user=request.user, class_group=obj, user_status=Membership.Status.ADMIN
            ).exists()
        return False

class RetrieveUpdateClassGroupView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsClassGroupMemberOrAdmin]
    serializer_class = ClassGroupSerializer
    queryset = ClassGroup.objects.all() 


# ==============================================================================
# APPROCHE 2 : APIView simple (Sans la magie de RetrieveUpdateAPIView)
# ==============================================================================
# Tout est explicite. Idéal si tu n'aimes pas que le framework cache des choses.
# C'est paradoxalement "plus propre" pour certains développeurs car le flux 
# de données est lisible de haut en bas sans avoir besoin de connaître le framework.

class ManualClassGroupView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        group = get_object_or_404(ClassGroup, pk=pk)
        # Vérification d'accès global (toute méthode nécessite d'être membre)
        if not Membership.objects.filter(user=user, class_group=group).exists():
            raise PermissionDenied("Vous n'êtes pas membre de ce groupe.")
        return group

    def get(self, request, pk):
        group = self.get_object(pk, request.user)  # Fetch et filtre
        serializer = ClassGroupSerializer(group)
        return Response(serializer.data)

    def put(self, request, pk):
        group = self.get_object(pk, request.user)
        
        # Vérification stricte pour la modification
        is_admin = request.user.is_superuser or Membership.objects.filter(
            user=request.user, class_group=group, user_status=Membership.Status.ADMIN
        ).exists()
        
        if not is_admin:
            raise PermissionDenied("Seuls les administrateurs du groupe peuvent le modifier.")

        serializer = ClassGroupSerializer(group, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# APPROCHE 3 : Surcharge de get_queryset et perform_update (Sécurité par filtrage)
# ==============================================================================
# Au lieu de renvoyer une erreur 403 (PermissionDenied) pour un "Read", 
# on filtre les objets à la base. Si un non-membre tente de lire un groupe,
# il recevra une erreur 404 (Non Trouvé) au lieu d'une 403 (Accès Refusé).
# Cela permet de cacher l'existence même du groupe.

class QuerysetClassGroupView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ClassGroupSerializer

    def get_queryset(self):
        # Le Retrieve est filtré ici : Django ne trouvera l'objet que si l'user est dedans
        return ClassGroup.objects.filter(users=self.request.user)

    def perform_update(self, serializer):
        # L'Update récupère l'objet valide depuis get_queryset, puis on fait une ultime vérification
        group = self.get_object() 
        is_admin = self.request.user.is_superuser or Membership.objects.filter(
            user=self.request.user, class_group=group, user_status=Membership.Status.ADMIN
        ).exists()

        if not is_admin:
            raise PermissionDenied("Seuls les administrateurs du groupe peuvent le modifier.")
            
        serializer.save()
