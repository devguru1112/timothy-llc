from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import OutreachTemplate, OutreachMessage
from .serializers import OutreachTemplateSerializer, OutreachMessageSerializer
from .services import OutreachService

class OutreachTemplateViewSet(viewsets.ModelViewSet):
    queryset = OutreachTemplate.objects.all()
    serializer_class = OutreachTemplateSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_default']


class OutreachMessageViewSet(viewsets.ModelViewSet):
    queryset = OutreachMessage.objects.select_related('project', 'user', 'template').all()
    serializer_class = OutreachMessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'project', 'user']
    
    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Send an outreach message."""
        message = self.get_object()
        if message.status != 'draft':
            return Response(
                {'error': 'Message has already been sent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        outreach_service = OutreachService()
        result = outreach_service.send_message(message)
        
        if result['success']:
            return Response({'status': 'sent', 'message_id': message.id})
        else:
            return Response(
                {'error': result.get('error', 'Failed to send message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def create_and_send(self, request):
        """Create and immediately send an outreach message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save(user=request.user, status='draft')
        
        outreach_service = OutreachService()
        result = outreach_service.send_message(message)
        
        if result['success']:
            return Response(OutreachMessageSerializer(message).data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'error': result.get('error', 'Failed to send message')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
