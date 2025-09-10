from django.urls import path
from .views import IncomingCallView, OutgoingCallView, TwilioTokenView, CallPageView, ReceiveCallPageView

urlpatterns = [
    path('incoming/', IncomingCallView.as_view(), name='incoming_call'),
    path('outgoing/', OutgoingCallView.as_view(), name='outgoing_call'),
    path('token/', TwilioTokenView.as_view(), name='twilio_token'),
    path('call/', CallPageView.as_view(), name='call_page'),
    path('receive/', ReceiveCallPageView.as_view(), name='receive_page'),
]