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
# APPROCHE 4 : Opérateurs Logiques (OU / ET) & Permissions par méthode
# ==============================================================================

class IsGroupMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # On vérifie seulement la qualité de membre (pour Retrieve)
        return Membership.objects.filter(user=request.user, class_group=obj).exists()

class IsGroupAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # On vérifie si la personne est admin du groupe (pour Update)
        return Membership.objects.filter(
            user=request.user, 
            class_group=obj, 
            user_status=Membership.Status.ADMIN
        ).exists()


class OperatorClassGroupView(RetrieveUpdateAPIView):
    # DRF ne possède pas d'attribut "retrieve_permission_classes" ou 
    # "update_permission_classes". Pour avoir des permissions différentes 
    # selon la méthode HTTP utilisée, il faut redéfinir la méthode `get_permissions()`.
    
    serializer_class = ClassGroupSerializer
    queryset = ClassGroup.objects.all()

    def get_permissions(self):
        # L'utilisateur doit TOUJOURS être authentifié
        # Astuce : On instancie la classe avec ()
        base_permissions = [IsAuthenticated()]
        
        # === Pour la méthode RETRIEVE (GET) ===
        if self.request.method in permissions.SAFE_METHODS: 
            return base_permissions + [IsGroupMember()]
            
        # === Pour les méthodes UPDATE (PUT, PATCH) ===
        elif self.request.method in ['PUT', 'PATCH']:
            # Exemple d'utilisation du "OU" (|)
            # Depuis DRF 3.9, on peut combiner des permissions avec | (OU), & (ET) et ~ (NON)
            # Attention: Le .is_superuser n'existe pas de base dans les permissions DRF,
            # (DRF a IsAdminUser qui vérifie is_staff). Pour faire ça proprement en DRF pur,
            # on utilise la permission par défaut IsAdminUser de DRF.
            # L'opération bitwise (|) renvoie une NOUVELLE instance de permission.
            
            from rest_framework.permissions import IsAdminUser
            # On exige (Etre Authentifié) ET (Etre Admin Global OU Etre Admin du Groupe)
            return base_permissions + [IsAdminUser() | IsGroupAdmin()]
            
        # Fallback de base au cas où (par exemple pour DELETE)
        return super().get_permissions()
