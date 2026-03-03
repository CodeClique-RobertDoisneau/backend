from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from apps.courses.views import ChapterViewSet, SectionViewSet, ItemViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

router = routers.SimpleRouter()
router.register('chapter', ChapterViewSet, 'chapter')
router.register('section', SectionViewSet, 'section')
router.register('item', ItemViewSet, 'item')

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
