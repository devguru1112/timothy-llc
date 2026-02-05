from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectLeadViewSet, SourcePlatformViewSet, ProjectMatchViewSet

router = DefaultRouter()
router.register(r'leads', ProjectLeadViewSet, basename='projectlead')
router.register(r'platforms', SourcePlatformViewSet, basename='sourceplatform')
router.register(r'matches', ProjectMatchViewSet, basename='projectmatch')

urlpatterns = [
    path('', include(router.urls)),
]
