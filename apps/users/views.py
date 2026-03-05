from django.http import Http404
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from yaml import serialize_all

from apps.users.models import User, ClassGroup
from apps.users.permissions import IsGroupMember, IsTeacher
from apps.users.serializers import UserListSerializer, UserDetailSerializer, ClassGroupSerializer


class UserList(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = UserListSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserDetailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

class UserDetail(APIView):

    serializer_class = UserDetailSerializer

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserDetailSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserDetailSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserMe(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get(self, request, format=None):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def put(self, request, format=None):
        serializer = UserDetailSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateClassGroupView(CreateAPIView):
    permission_classes = [IsAuthenticated, (IsTeacher | IsAdminUser)]
    serializer_class = ClassGroupSerializer
    queryset = ClassGroup.objects.all()

class RetrieveUpdateClassGroupView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, (IsGroupMember | IsAdminUser)]
    serializer_class = ClassGroupSerializer
    queryset = ClassGroup.objects.all()






