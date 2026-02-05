"""
Service for handling outreach operations.
"""
import logging
from django.utils import timezone
from .models import OutreachMessage
from .email_service import get_email_service
from projects.models import ProjectLead

logger = logging.getLogger(__name__)


class OutreachService:
    """Handles sending and tracking outreach messages."""
    
    def send_message(self, message: OutreachMessage) -> dict:
        """
        Send an outreach message using configured email service.
        """
        try:
            email_service = get_email_service()
            result = email_service.send_email(
                to_email=message.recipient_email,
                subject=message.subject,
                body=message.body,
                from_email=None  # Will use default from email service
            )
            
            if result.get('success'):
                message.status = 'sent'
                message.sent_at = timezone.now()
                if result.get('message_id'):
                    message.notes = f"Email service message ID: {result.get('message_id')}"
                message.save()
                
                # Update project status
                if message.project.status == 'qualified':
                    message.project.status = 'contacted'
                    message.project.contacted_at = timezone.now()
                    message.project.save()
                
                logger.info(f"Outreach message sent: {message.id} to {message.recipient_email}")
                return {'success': True, 'message_id': message.id}
            else:
                message.status = 'draft'  # Keep as draft if sending failed
                message.notes = f"Failed to send: {result.get('error', 'Unknown error')}"
                message.save()
                return {'success': False, 'error': result.get('error', 'Failed to send email')}
            
        except Exception as e:
            logger.error(f"Error sending outreach message {message.id}: {e}")
            message.status = 'draft'
            message.notes = f"Error: {str(e)}"
            message.save()
            return {'success': False, 'error': str(e)}
    
    def generate_message_from_template(self, project: ProjectLead, template, user) -> dict:
        """Generate outreach message from template with project data."""
        subject = template.subject.format(
            project_title=project.title,
            company_name=project.company_name or 'your company'
        )
        
        body = template.body.format(
            recipient_name=project.contact_name or 'there',
            project_title=project.title,
            company_name=project.company_name or 'your company',
            user_name=user.get_full_name() or user.username,
            user_email=user.email,
            portfolio_url=user.portfolio_url or ''
        )
        
        return {
            'subject': subject,
            'body': body
        }
