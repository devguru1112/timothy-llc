from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScrapingJobViewSet

router = DefaultRouter()
router.register(r'jobs', ScrapingJobViewSet, basename='scrapingjob')

urlpatterns = [
    path('', include(router.urls)),
]
