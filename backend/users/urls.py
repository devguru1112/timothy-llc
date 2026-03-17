from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import UserRegistrationView, UserProfileView, UserProfilePhotoView
from .verification_views import (
    SendPhoneVerificationView, VerifyPhoneView,
    SendEmailVerificationView, VerifyEmailView
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/photo/', UserProfilePhotoView.as_view(), name='profile_photo'),
    path('verify/phone/send/', SendPhoneVerificationView.as_view(), name='send_phone_verification'),
    path('verify/phone/', VerifyPhoneView.as_view(), name='verify_phone'),
    path('verify/email/send/', SendEmailVerificationView.as_view(), name='send_email_verification'),
    path('verify/email/', VerifyEmailView.as_view(), name='verify_email'),
]
