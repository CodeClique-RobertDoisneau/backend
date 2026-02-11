from rest_framework.serializers import ModelSerializer

from apps.courses.models import Chapter, Section, Item


class ItemListSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ['id', 'title', 'item_type', 'difficulty']


class ItemDetailSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = ['id', 'title', 'item_type', 'content', 'difficulty', 'created_at', 'modified_at']


class SectionListSerializer(ModelSerializer):

    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'difficulty']


class SectionDetailSerializer(ModelSerializer):

    items = ItemListSerializer(many=True, read_only=True)
    class Meta:
        model = Section
        fields = ['id', 'title', 'description', 'difficulty', 'created_at', 'modified_at', 'items']


class ChapterListSerializer(ModelSerializer):

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'grade_level']


class ChapterDetailSerializer(ModelSerializer):
    sections = SectionListSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'description', 'grade_level', 'created_at', 'modified_at', 'sections']