import os
import requests
from openai import OpenAI
from django.conf import settings
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import serializers

from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from drf_spectacular.types import OpenApiTypes

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
from django.http import HttpResponse
from dotenv import load_dotenv
from rest_framework.permissions import AllowAny
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from django.views import View
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import IsAdmin
from apps.home.serializers import PurchaseNumberSerializer
from apps.users.models.agent_model import AgentModel
from apps.users.models.lead_model import LeadModel, LeadEmailModel
from apps.aiModule.utils.util_model import save_call_message
from apps.aiModule.utils.follow_up import refreshAI
from apps.home.utils.summary_email import send_summary_email



load_dotenv(override=True)

sid = os.getenv("TWILIO_ACCOUNT_SID")
token = os.getenv("TWILIO_AUTH_TOKEN")
twilioNumber = os.getenv("TWILIO_NUMBER")
toNumber = os.getenv("TO_NUMBER")
api_key_sid = os.getenv("TWILIO_API_KEY_SID")
api_key_secret = os.getenv("TWILIO_API_KEY_SECRET")
twilml_app_sid = os.getenv("TWILML_APP_SID")

client = Client(sid, token)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VoiceResponseView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Generate TwiML Voice Response",
        description="Generates a TwiML response to dial a number. This is typically used by Twilio's webhook.",
        parameters=[
            OpenApiParameter(name='To', description='The phone number to dial.',
                             required=True, type=OpenApiTypes.STR),
            OpenApiParameter(name='From', description='The caller ID. Defaults to the configured Twilio number.',
                             required=False, type=OpenApiTypes.STR),
        ],
        responses={200: OpenApiTypes.STR}
    )
    def get(self, request):
        to_number = request.GET.get("To")
        from_number = request.GET.get("From", twilioNumber)
        response = VoiceResponse()
        # response.record(play_beep=True, recording_status_callback='/temp/recording-status/', recording_status_callback_method='POST')
        if to_number:
            response.dial(
                number=to_number,
                caller_id=from_number,
                record=True,
                recording_status_callback='/temp/recording-status/',
                recording_status_callback_method='POST')
        else:
            response.say("Thanks for calling! No destination number provided.")

        print(str(response))
        return HttpResponse(str(response), content_type="text/xml")

    def post(self, request):
        """Handle incoming voice requests"""
        try:
            print(f"Response from POST: {request.data}")
            response = VoiceResponse()
            dial = response.dial(caller_id=twilioNumber)
            dial.client("browser-user")
            print(str(response))
            return HttpResponse(str(response), content_type="text/xml")
        except Exception as e:
            return Response(
                {"error": "Failed to process voice request"},
                status=HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwilioTokenView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary='Generate Token for Twilio Token',
        parameters=[
            OpenApiParameter(name='identity', required=False,type=OpenApiTypes.STR)
        ],
        responses={200: inline_serializer(
            name='TokenResponse',
            fields={
                'token': serializers.CharField(help_text='JWT Token')
            }
        )}
    )
    def get(self, request):
        identity = request.GET.get('identity', "browser-user")

        token = AccessToken(
            sid, api_key_sid, api_key_secret, identity=identity, ttl=3600)
        voice_grant = VoiceGrant(outgoing_application_sid=twilml_app_sid)
        token.add_grant(voice_grant)

        return Response({"token": token.to_jwt()})


class PhoneCallView(View):
    def get(self, request):
        return render(request, 'callFrom.html')


class CallView(View):
    def get(self, request):
        return render(request, 'call.html')


class RecordingStatusView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        exclude=True
    )
    def post(self, request):
        print(f"Data from request: {request.data}")
        recording_sid = request.data.get('RecordingSid')
        recording_url = request.data.get('RecordingUrl')
        call_sid = request.data.get('CallSid')
        child_calls = client.calls.list(parent_call_sid=call_sid)

        if not recording_url:
            return Response({"error": "RecordingUrl not found in request"}, status=400)
        recording_url += '.mp3'

        lead_id = None
        for leg in child_calls:
            from_num = leg._from
            to_num = leg.to
            
            lead = LeadModel.objects.filter(leadphonemodel__phone_number=to_num).first()
            if lead:
                lead_id = lead.id
                break

            lead = LeadModel.objects.filter(leadphonemodel__phone_number=from_num).first()
            if lead:
                lead_id = lead.id
                break
        
        if not lead_id:
            return Response({'error': 'Lead not found for this call'}, status=HTTP_400_BAD_REQUEST)
    

        try:
            response = requests.get(recording_url, auth=(sid, token))
            response.raise_for_status()  # Raise an exception for bad status codes

            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=(f"{recording_sid}.mp3", response.content)
            )

            save_call_message(lead_id, transcript.text)

            # Send summary email to lead
            try:
                lead = LeadModel.objects.get(id=lead_id)
                agent = lead.assign_to
                if not agent:
                    return Response({'Error': 'Agent not assigned to this lead'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
            except LeadModel.DoesNotExist:
                return Response({'Error': 'Lead not found'}, status=HTTP_404_NOT_FOUND)

            emailModel = LeadEmailModel.objects.filter(lead__id=lead_id).first()
            if not emailModel:
                return Response({'Error': 'Email not found For Summary'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            if not send_summary_email(transcript.text, agent.smtp_email, agent.smtp_password, emailModel.email):
                return Response({'Error': f'Email Summary not sent for Lead of id {lead_id}'})

            try:
                refreshAI(lead_id)
            except Exception as e:
                return Response({'Error': f'Error in refreshing Lead of id {lead_id}'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                'status': 'success',
                'transcript': transcript.text
            }, status=HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to download recording: {e}"}, status=500)
        except Exception as e:
            # Log the exception for debugging
            print(f"An error occurred: {e}")
            return Response({"error": "An error occurred during transcription"}, status=500)


class TwilioBuyNumber(APIView):
    # permission_classes = [IsAdmin]

    @extend_schema(
        summary='Get Available Phone Numbers',
        parameters=[
            OpenApiParameter(name='country', required=False, type=OpenApiTypes.STR)
        ],
        responses={200: inline_serializer(
            name='AvailableNumbersResponse',
            fields={
                'available_numbers': serializers.ListField(child=serializers.CharField())
            }
        )}
    )
    def get(self, request):
        country = request.GET.get('country', 'US')

        available_numbers = client.available_phone_numbers(
            country).local.list(limit=20)

        return Response({
            'available_numbers': [number.phone_number for number in available_numbers]
        }, status=HTTP_200_OK)

    @extend_schema(
        summary='Purchase a Phone Number',
        request=PurchaseNumberSerializer,
    )
    def post(self, request):
        number = request.data.get('number')
        country = request.data.get('country')
        if not number:
            return Response({'error': 'Number is required'}, status=HTTP_400_BAD_REQUEST)
        try:
            if country == "GB":
                address = client.addresses.create(
                    customer_name='Customer Name',
                    street='123 Main St',
                    city='London',
                    region='ENG',
                    postal_code='SW1A 1AA',
                    iso_country='GB'
                )
                purchased_number = client.incoming_phone_numbers.create(
                    phone_number=number,
                    address_sid=address.sid
                )
            else:
                purchased_number = client.incoming_phone_numbers.create(
                    phone_number=number,
                )
            return Response({
                'message': 'Number purchased successfully',
                'purchased_number': purchased_number.phone_number
            }, status=HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)
