from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from apps.courses.views import ChapterViewSet, SectionViewSet, ItemViewSet

router = routers.SimpleRouter()
router.register('chapter', ChapterViewSet, 'chapter')
router.register('section', SectionViewSet, 'section')
router.register('item', ItemViewSet, 'item')

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include(router.urls))
]
