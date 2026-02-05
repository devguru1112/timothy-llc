from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OutreachTemplateViewSet, OutreachMessageViewSet

router = DefaultRouter()
router.register(r'templates', OutreachTemplateViewSet, basename='outreachtemplate')
router.register(r'messages', OutreachMessageViewSet, basename='outreachmessage')

urlpatterns = [
    path('', include(router.urls)),
]
