from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import GenericViewSet

from apps.courses.models import Node
from apps.courses.serializers import NodeSerializer, NodeAnswersSerializer


class NodeViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):

    serializer_class = NodeSerializer
    queryset = Node.objects.all()

    @action(detail=True, methods=['POST'], url_path='answer')
    def answer(self, request, pk):



        serializer = NodeAnswersSerializer(self.get_object())
        return Response(serializer.data, status=HTTP_200_OK)




