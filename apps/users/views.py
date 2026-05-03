import random
import string

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from apps.users.models import User, ClassGroup, Membership
from apps.users.permissions import IsGroupMember, IsTeacher, IsGroupAdmin, IsMembershipGroupAdmin
from apps.users.serializers import UserSerializer, ClassGroupSerializer, MembershipSerializer


class UserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action in ['retrieve', 'update']:
            self.permission_classes += [IsAdminUser]

        return super().get_permissions()

    @action(detail=False, methods = ['GET', 'PUT'])
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user, context=self.get_serializer_context())
            return Response(serializer.data)
        else: # request.method == 'put'
            serializer = UserSerializer(request.user, data=request.data, context=self.get_serializer_context())
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods = ['POST'], url_path='me/join-group')
    def me_join_group(self, request):
        join_code = request.data.get('join_code')

        if not join_code:
            return Response(
                {"detail": "Veuillez fournir un code d'invitation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            class_group = ClassGroup.objects.get(join_code=join_code)

            membership, created = Membership.objects.get_or_create(
                user=request.user,
                class_group=class_group,
                defaults={'user_status': Membership.Status.MEMBER}
            )

            # Si l'utilisateur était déjà dans le groupe
            if not created:
                return Response(
                    {"detail": "Vous êtes déjà membre de ce groupe."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Sinon l'utilisateur a été ajouté dans le groupe avec succès
            return Response(
                {"detail": "Vous avez rejoint le groupe avec succès.", "group_id": class_group.pk},
                status=status.HTTP_201_CREATED
            )

        except ClassGroup.DoesNotExist:
            # Le join_code est invalide
            return Response(
                {"detail": "Ce code d'invitation est invalide."},
                status=status.HTTP_404_NOT_FOUND
            )

class ClassGroupViewSet(CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):

    serializer_class = ClassGroupSerializer
    queryset = ClassGroup.objects.all()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action == 'create':
            self.permission_classes += [IsTeacher]
        elif self.action == 'retrieve':
            self.permission_classes += [IsGroupMember]
        elif self.action in ['update', 'join_code']:
            self.permission_classes += [IsGroupAdmin]
        else:
            self.permission_classes += [IsAdminUser]
        return super().get_permissions()

    @action(detail=True, methods=['POST', 'DELETE'], url_path='join-code')
    def join_code(self, request, pk):
        class_group = self.get_object()

        if request.method == 'POST':
            if not class_group.join_code:
                chars = string.ascii_uppercase + string.digits

                # Boucle pour s'assurer de l'unicité du code
                while True:
                    new_code = ''.join(random.choice(chars) for _ in range(6))
                    # On sort de la boucle si aucun groupe n'a ce code
                    if not ClassGroup.objects.filter(join_code=new_code).exists():
                        break

                class_group.join_code = new_code
                class_group.save(update_fields=['join_code'])

                return Response({'join_code': class_group.join_code}, status=status.HTTP_200_OK)

            else:
                return Response({'join_code': class_group.join_code}, status=status.HTTP_200_OK)
        else : # request.method == 'DELETE'
            class_group.join_code = None
            class_group.save(update_fields=['join_code'])

            return Response(status=status.HTTP_204_NO_CONTENT)

class MembershipViewSet(ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer
    # Permet au front de faire : GET /api/memberships/?class_group=5
    filterset_fields = ['class_group', 'user']

    def get_queryset(self):
        user = self.request.user
        # Seuls les administrateurs (du site) peuvent voir tous les memberships
        if user.is_staff or user.is_superuser:
            return self.queryset
        # Les membres d'un groupe ne peuvent voir que les memberships de leur groupe
        return self.queryset.filter(class_group__users=user)

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        # Seul un admin du ClassGroup peut update, partial_update et delete un membership
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes += [IsMembershipGroupAdmin]
        return super().get_permissions()






