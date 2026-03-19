from django.urls import path

from .views import CreateTopUpView, PayPalCaptureView, stripe_webhook, coinbase_webhook


urlpatterns = [
    path("topups/create/", CreateTopUpView.as_view(), name="create_topup"),
    path("topups/<int:topup_id>/paypal/capture/", PayPalCaptureView.as_view(), name="paypal_capture"),
    path("webhooks/stripe/", stripe_webhook, name="stripe_webhook"),
    path("webhooks/coinbase/", coinbase_webhook, name="coinbase_webhook"),
]

