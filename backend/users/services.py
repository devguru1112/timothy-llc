"""
Services for user verification (SMS and Email).
"""
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def send_sms_verification(phone: str, code: str) -> Dict[str, bool]:
    """
    Send SMS verification code.
    Supports Twilio, AWS SNS, and other SMS providers.
    """
    sms_provider = os.getenv('SMS_PROVIDER', 'twilio').lower()
    
    if sms_provider == 'twilio':
        return _send_via_twilio(phone, code)
    elif sms_provider == 'aws_sns':
        return _send_via_aws_sns(phone, code)
    else:
        # For development/testing, just log the code
        logger.info(f"SMS Verification Code for {phone}: {code}")
        return {'success': True, 'message': 'Code logged (development mode)'}


def _send_via_twilio(phone: str, code: str) -> Dict[str, bool]:
    """Send SMS via Twilio."""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            logger.warning("Twilio credentials not configured, logging code instead")
            logger.info(f"SMS Verification Code for {phone}: {code}")
            return {'success': True, 'message': 'Code logged (Twilio not configured)'}
        
        # Uncomment when twilio package is installed
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(
        #     body=f'Your verification code is: {code}',
        #     from_=from_number,
        #     to=phone
        # )
        # logger.info(f"Sent SMS verification to {phone} via Twilio")
        # return {'success': True, 'message_id': message.sid}
        
        # Placeholder for now
        logger.info(f"Twilio SMS Verification Code for {phone}: {code}")
        return {'success': True, 'message': 'Code logged (Twilio placeholder)'}
        
    except Exception as e:
        logger.error(f"Error sending SMS via Twilio: {e}")
        return {'success': False, 'error': str(e)}


def _send_via_aws_sns(phone: str, code: str) -> Dict[str, bool]:
    """Send SMS via AWS SNS."""
    try:
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        if not all([aws_access_key, aws_secret_key]):
            logger.warning("AWS SNS credentials not configured, logging code instead")
            logger.info(f"SMS Verification Code for {phone}: {code}")
            return {'success': True, 'message': 'Code logged (AWS SNS not configured)'}
        
        # Uncomment when boto3 is installed
        # import boto3
        # sns_client = boto3.client(
        #     'sns',
        #     aws_access_key_id=aws_access_key,
        #     aws_secret_access_key=aws_secret_key,
        #     region_name=aws_region
        # )
        # response = sns_client.publish(
        #     PhoneNumber=phone,
        #     Message=f'Your verification code is: {code}'
        # )
        # logger.info(f"Sent SMS verification to {phone} via AWS SNS")
        # return {'success': True, 'message_id': response['MessageId']}
        
        # Placeholder for now
        logger.info(f"AWS SNS SMS Verification Code for {phone}: {code}")
        return {'success': True, 'message': 'Code logged (AWS SNS placeholder)'}
        
    except Exception as e:
        logger.error(f"Error sending SMS via AWS SNS: {e}")
        return {'success': False, 'error': str(e)}


def send_email_verification(email: str, code: str) -> Dict[str, bool]:
    """
    Send email verification code.
    Uses the email service from outreach app.
    """
    try:
        from outreach.email_service import get_email_service
        
        email_service = get_email_service()
        subject = "Email Verification Code"
        body = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Your verification code is: <strong>{code}</strong></p>
            <p>This code will expire in 24 hours.</p>
            <p>If you didn't request this code, please ignore this email.</p>
        </body>
        </html>
        """
        
        result = email_service.send_email(
            to_email=email,
            subject=subject,
            body=body
        )
        
        if result.get('success'):
            logger.info(f"Sent email verification to {email}")
            return {'success': True}
        else:
            logger.error(f"Failed to send email verification: {result.get('error')}")
            return {'success': False, 'error': result.get('error')}
            
    except Exception as e:
        logger.error(f"Error sending email verification: {e}")
        return {'success': False, 'error': str(e)}
