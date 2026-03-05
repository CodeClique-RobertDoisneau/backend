from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

from apps.courses.models import Node
from apps.courses.serializers import NodeSerializer


class NodeViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet):

    serializer_class = NodeSerializer
    queryset = Node.objects.all()


