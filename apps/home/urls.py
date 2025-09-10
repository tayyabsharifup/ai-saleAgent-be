
from django.urls import path
from .views import (
    VoiceResponseView,
    TwilioTokenView,
    PhoneCallView,
    RecordingStatusView,
    TwilioBuyNumber,
    ReceiveCallView,
)

urlpatterns = [
    path("voice_response/", VoiceResponseView.as_view(), name="voice_response"),
    path("token/", TwilioTokenView.as_view(), name='voice-token'),
    path('phone_view/', PhoneCallView.as_view(), name='phone-call'),
    path('receive_call/', ReceiveCallView.as_view(), name='receive-call'),
    path('recording-status/', RecordingStatusView.as_view(), name='recording-status'),
    path('buy-number/', TwilioBuyNumber.as_view(), name='buy-number'),
]
