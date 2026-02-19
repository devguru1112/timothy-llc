from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectLeadViewSet, SourcePlatformViewSet, ProjectMatchViewSet,
    ProjectApplicationViewSet, SystemSettingsViewSet, JobCategoryViewSet,
    ScrapingConfigViewSet
)

router = DefaultRouter()
router.register(r'leads', ProjectLeadViewSet, basename='projectlead')
router.register(r'platforms', SourcePlatformViewSet, basename='sourceplatform')
router.register(r'matches', ProjectMatchViewSet, basename='projectmatch')
router.register(r'applications', ProjectApplicationViewSet, basename='projectapplication')
router.register(r'settings', SystemSettingsViewSet, basename='systemsettings')
router.register(r'categories', JobCategoryViewSet, basename='jobcategory')
router.register(r'scraping-configs', ScrapingConfigViewSet, basename='scrapingconfig')

urlpatterns = [
    path('', include(router.urls)),
]
