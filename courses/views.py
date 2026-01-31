from rest_framework.viewsets import ReadOnlyModelViewSet

from courses.models import Chapter, Section, Item
from courses import serializers



class MultipleSerializerMixin:

    detail_serializer_class = None

    def get_serializer_class(self):

        if self.action == 'retrieve' and self.detail_serializer_class is not None:
            # Si l'action demandée est le détail alors nous retournons le serializer de détail
            return self.detail_serializer_class

        return super().get_serializer_class()

class ChapterViewSet(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = serializers.ChapterListSerializer
    detail_serializer_class = serializers.ChapterDetailSerializer

    def get_queryset(self):
        return Chapter.objects.all()


class SectionViewSet(MultipleSerializerMixin, ReadOnlyModelViewSet):

    serializer_class = serializers.SectionListSerializer
    detail_serializer_class = serializers.SectionDetailSerializer

    def get_queryset(self):
        return Section.objects.all()

class ItemViewSet(ReadOnlyModelViewSet):

    serializer_class = serializers.ItemListSerializer
    detail_serializer_class = serializers.ItemDetailSerializer

    def get_queryset(self):
        return Item.objects.all()
