from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScrapingJobViewSet, scraping_schedule

router = DefaultRouter()
router.register(r'jobs', ScrapingJobViewSet, basename='scrapingjob')

urlpatterns = [
    path('schedule/', scraping_schedule),
    path('', include(router.urls)),
]
