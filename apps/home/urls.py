
from django.urls import path
# from .views import HomeView, MakeCallView, voice_response
from .views import (
    VoiceResponseView,
    TwilioTokenView,
    PhoneCallView,
    CallView,
    RecordingStatusView,
    TwilioBuyNumber,
)

urlpatterns = [
    path("voice_response/", VoiceResponseView.as_view(), name="voice_response"),
    path("token/", TwilioTokenView.as_view(), name='voice-token'),
    path('phone_view/', PhoneCallView.as_view(), name='phone-call'),
    path('call/', CallView.as_view(), name='call'),
    path('recording-status/', RecordingStatusView.as_view(), name='recording-status'),
    path('buy-number/', TwilioBuyNumber.as_view(), name='buy-number'),
]
