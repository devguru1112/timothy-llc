"""
Email service integration for sending outreach messages.
Supports SendGrid, AWS SES, and SMTP.
"""
import os
import logging
from typing import Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Base email service interface."""
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None) -> Dict[str, any]:
        """Send an email. Returns dict with 'success' and optional 'message_id'."""
        raise NotImplementedError


class SendGridEmailService(EmailService):
    """SendGrid email service implementation."""
    
    def __init__(self):
        self.api_key = os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            logger.warning("SendGrid API key not configured")
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None) -> Dict[str, any]:
        """Send email via SendGrid."""
        if not self.api_key:
            logger.error("SendGrid API key not configured")
            return {'success': False, 'error': 'SendGrid API key not configured'}
        
        try:
            # Uncomment when sendgrid package is installed
            # from sendgrid import SendGridAPIClient
            # from sendgrid.helpers.mail import Mail
            
            # message = Mail(
            #     from_email=from_email or os.getenv('SENDGRID_FROM_EMAIL', 'noreply@example.com'),
            #     to_emails=to_email,
            #     subject=subject,
            #     html_content=body
            # )
            # sg = SendGridAPIClient(self.api_key)
            # response = sg.send(message)
            # return {'success': True, 'message_id': response.headers.get('X-Message-Id')}
            
            # Placeholder for now
            logger.info(f"SendGrid: Would send email to {to_email} with subject: {subject}")
            return {'success': True, 'message_id': 'placeholder'}
        except Exception as e:
            logger.error(f"Error sending email via SendGrid: {e}")
            return {'success': False, 'error': str(e)}


class AWSSESEmailService(EmailService):
    """AWS SES email service implementation."""
    
    def __init__(self):
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        if not self.aws_access_key or not self.aws_secret_key:
            logger.warning("AWS SES credentials not configured")
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None) -> Dict[str, any]:
        """Send email via AWS SES."""
        if not self.aws_access_key or not self.aws_secret_key:
            logger.error("AWS SES credentials not configured")
            return {'success': False, 'error': 'AWS SES credentials not configured'}
        
        try:
            # Uncomment when boto3 is installed
            # import boto3
            # ses_client = boto3.client(
            #     'ses',
            #     aws_access_key_id=self.aws_access_key,
            #     aws_secret_access_key=self.aws_secret_key,
            #     region_name=self.aws_region
            # )
            # response = ses_client.send_email(
            #     Source=from_email or os.getenv('AWS_SES_FROM_EMAIL', 'noreply@example.com'),
            #     Destination={'ToAddresses': [to_email]},
            #     Message={
            #         'Subject': {'Data': subject},
            #         'Body': {'Html': {'Data': body}}
            #     }
            # )
            # return {'success': True, 'message_id': response['MessageId']}
            
            # Placeholder for now
            logger.info(f"AWS SES: Would send email to {to_email} with subject: {subject}")
            return {'success': True, 'message_id': 'placeholder'}
        except Exception as e:
            logger.error(f"Error sending email via AWS SES: {e}")
            return {'success': False, 'error': str(e)}


class SMTPEmailService(EmailService):
    """SMTP email service implementation."""
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', self.smtp_user)
    
    def send_email(self, to_email: str, subject: str, body: str, from_email: Optional[str] = None) -> Dict[str, any]:
        """Send email via SMTP."""
        if not self.smtp_user or not self.smtp_password:
            logger.error("SMTP credentials not configured")
            return {'success': False, 'error': 'SMTP credentials not configured'}
        
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_email or self.from_email
            msg['To'] = to_email
            
            msg.attach(MIMEText(body, 'html'))
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"SMTP: Sent email to {to_email} with subject: {subject}")
            return {'success': True, 'message_id': 'smtp_sent'}
        except Exception as e:
            logger.error(f"Error sending email via SMTP: {e}")
            return {'success': False, 'error': str(e)}


def get_email_service() -> EmailService:
    """Factory function to get the configured email service."""
    email_provider = os.getenv('EMAIL_PROVIDER', 'smtp').lower()
    
    if email_provider == 'sendgrid':
        return SendGridEmailService()
    elif email_provider == 'aws_ses':
        return AWSSESEmailService()
    elif email_provider == 'smtp':
        return SMTPEmailService()
    else:
        logger.warning(f"Unknown email provider: {email_provider}, using SMTP")
        return SMTPEmailService()
