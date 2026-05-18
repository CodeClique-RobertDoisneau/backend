from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from apps.courses.views import NodeViewSet, NodeLinkViewSet, ClassGroupSyllabusViewSet
from apps.users.views import UserViewSet, ClassGroupViewSet, MembershipViewSet
from apps.records.views import ProgressViewSet

router = routers.SimpleRouter()
router.register('class-groups', ClassGroupViewSet)
router.register('users', UserViewSet)
router.register('nodes', NodeViewSet)
router.register('memberships', MembershipViewSet)
router.register('nodelinks', NodeLinkViewSet)
router.register('classgroupsyllabus', ClassGroupSyllabusViewSet)
router.register('progress', ProgressViewSet)

urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/auth/', include("rest_framework.urls", namespace="rest_framework")),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
