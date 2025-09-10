import os
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from twilio.twiml.voice_response import VoiceResponse
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_NUMBER')
api_key_sid = os.getenv('TWILIO_API_KEY_SID')
api_key_secret = os.getenv('TWILIO_API_KEY_SECRET')
twiml_app_sid = os.getenv('TWILML_APP_SID')


class IncomingCallView(APIView):
    """
    Handles incoming calls from Twilio.
    Returns TwiML to connect the call.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        response = VoiceResponse()
        response.say("Hello! Thank you for calling.")
        # You can add more logic here, like connecting to an agent
        return HttpResponse(str(response), content_type='text/xml')


class OutgoingCallView(APIView):
    """
    Handles outgoing calls initiated from the web client.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        to_number = request.GET.get('to')
        if not to_number:
            return Response({'error': 'Phone number required'}, status=400)

        response = VoiceResponse()
        response.dial(to_number, caller_id=twilio_number)
        return HttpResponse(str(response), content_type='text/xml')


class TwilioTokenView(APIView):
    """
    Generates access token for Twilio client-side calling.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        identity = request.GET.get('identity', 'user')

        token = AccessToken(account_sid, api_key_sid, api_key_secret, identity=identity, ttl=86400)  # 24 hours
        voice_grant = VoiceGrant(outgoing_application_sid=twiml_app_sid, incoming_allow=True)
        token.add_grant(voice_grant)

        return Response({'token': token.to_jwt()})


class CallPageView(View):
    """
    Renders the outgoing call page.
    """
    def get(self, request):
        return render(request, 'outgoing_call.html')


class ReceiveCallPageView(View):
    """
    Renders the incoming call page.
    """
    def get(self, request):
        return render(request, 'incoming_call.html')