"""
Views for phone and email verification.
"""
import os
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from .serializers import PhoneVerificationSerializer, EmailVerificationSerializer

User = get_user_model()


class SendPhoneVerificationView(generics.CreateAPIView):
    """Send phone verification code."""
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneVerificationSerializer
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        if not user.phone:
            return Response(
                {'error': 'Phone number not set'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if user.phone_verified:
            return Response(
                {'message': 'Phone already verified'},
                status=status.HTTP_200_OK
            )
        
        code = user.send_phone_verification_code()
        
        return Response({
            'message': 'Verification code sent to your phone',
            'code': code if os.getenv('DEBUG') == 'True' else None  # Only in debug mode
        })


class VerifyPhoneView(generics.CreateAPIView):
    """Verify phone with code."""
    permission_classes = [IsAuthenticated]
    serializer_class = PhoneVerificationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        user = request.user
        
        if user.verify_phone_code(code):
            return Response({
                'message': 'Phone verified successfully',
                'phone_verified': True
            })
        else:
            return Response(
                {'error': 'Invalid or expired verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )


class SendEmailVerificationView(generics.CreateAPIView):
    """Send email verification code."""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        
        if user.email_verified:
            return Response(
                {'message': 'Email already verified'},
                status=status.HTTP_200_OK
            )
        
        code = user.send_email_verification_code()
        
        return Response({
            'message': 'Verification code sent to your email',
            'code': code if os.getenv('DEBUG') == 'True' else None  # Only in debug mode
        })


class VerifyEmailView(generics.CreateAPIView):
    """Verify email with code."""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailVerificationSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        user = request.user
        
        if user.verify_email_code(code):
            return Response({
                'message': 'Email verified successfully',
                'email_verified': True
            })
        else:
            return Response(
                {'error': 'Invalid or expired verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )
