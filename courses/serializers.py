from rest_framework.serializers import ModelSerializer

from courses.models import Chapter, Section, Item


class ItemListSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ['id', 'title', 'level', 'difficulty']


class ItemDetailSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ['id', 'title', 'content', 'level', 'difficulty']


class SectionListSerializer(ModelSerializer):

    class Meta:
        model = Section
        fields = ['id', 'title']


class SectionDetailSerializer(ModelSerializer):

    items = ItemDetailSerializer(many=True, read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'title', 'level', 'difficulty', 'items']


class ChapterListSerializer(ModelSerializer):

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description']


class ChapterDetailSerializer(ModelSerializer):
    sections = SectionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'created_at', 'modified_at', 'sections']