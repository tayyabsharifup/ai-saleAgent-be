import os
import requests
from openai import OpenAI
from django.conf import settings
from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework import serializers




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
from apps.aiModule.models import NewLeadCall
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

twilio_push_credentials = os.getenv("TWILIO_PUSH_CREDENTIALS")

client = Client(sid, token)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class VoiceResponseView(APIView):
    permission_classes = [AllowAny]

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

        # print(str(response))
        print("Response from GET")
        return HttpResponse(str(response), content_type="text/xml")

    def post(self, request):
        """Handle both incoming and outgoing voice requests"""
        response = VoiceResponse()
        caller = request.data.get('Caller', '')
        direction = request.data.get('Direction')
        print("Response from POST")
        print(request.data)

        if caller.startswith('client:') or direction in ['outbound-api', 'outbound-dial']:
            # Outbound call from browser SDK (check Caller for client-initiated)
            print("Outbound call")
            to_number = request.data.get('To')
            from_number = request.data.get('From', twilioNumber)
            if to_number:
                response.dial(
                    number=to_number,
                    caller_id=from_number,
                    record=True,
                    recording_status_callback='/temp/recording-status/',
                    recording_status_callback_method='POST'
                )
            else:
                response.say("No destination number provided.")
        elif direction == 'inbound':
            # Incoming call to Twilio number
            print("Inbound call")
            to_number = request.data.get('To')  # The Twilio number receiving the call
            agent = AgentModel.objects.filter(phone=to_number).first()
            callback_url = '/temp/recording-status/'
            client_identity = "browser-user"
            if agent:
                callback_url += f'?agent_id={agent.id}'
                client_identity = f"agent-{agent.id}"
            print(f"Agent found: {agent is not None}, Client identity: {client_identity}")

            dial = response.dial(record=True, recording_status_callback=callback_url, recording_status_callback_method='POST')
            dial.client(client_identity)
        else:
            print("Unable to determine call direction.")
            response.say("Unable to determine call direction.")

        return HttpResponse(str(response), content_type="text/xml")


class TwilioTokenView(APIView):
    permission_classes = [AllowAny]

    
    def get(self, request):
        identity = request.GET.get('identity', "browser-user")

        token = AccessToken(
            sid, api_key_sid, api_key_secret, identity=identity, ttl=86400)
        voice_grant = VoiceGrant(outgoing_application_sid=twilml_app_sid, incoming_allow=True, push_credential_sid=twilio_push_credentials)
        token.add_grant(voice_grant)

        return Response({"token": token.to_jwt()})


class PhoneCallView(View):
    def get(self, request):
        return render(request, 'callFrom.html')


class ReceiveCallView(View):
    def get(self, request):
        return render(request, 'receive_call.html')


class RecordingStatusView(APIView):
    permission_classes = [AllowAny]

    
    def post(self, request):
        print(f"Data from request: {request.data}")
        recording_sid = request.data.get('RecordingSid')
        recording_url = request.data.get('RecordingUrl')
        call_sid = request.data.get('CallSid')
        child_calls = client.calls.list(parent_call_sid=call_sid)

        if not recording_url:
            return Response({"error": "RecordingUrl not found in request"}, status=400)
        recording_url += '.mp3'

        # Get agent from callback query params
        agent_id = request.GET.get('agent_id')
        agent = None
        if agent_id:
            try:
                agent = AgentModel.objects.get(id=agent_id)
            except AgentModel.DoesNotExist:
                pass

        lead_id = None
        from_num = None
        to_num = None
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

        if not lead_id and not from_num:
            return Response({'error': 'Lead not found for this call'}, status=HTTP_400_BAD_REQUEST)
    

        try:
            response = requests.get(recording_url, auth=(sid, token))
            response.raise_for_status()  # Raise an exception for bad status codes

            transcript = openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=(f"{recording_sid}.mp3", response.content)
            )

            if not lead_id:
                newLeadCall, is_created = NewLeadCall.objects.get_or_create(
                    is_map=False,
                    transcript=transcript.text,
                    from_num=from_num,
                    defaults={'agent': agent}
                )
                if not is_created and agent:
                    newLeadCall.agent = agent
                    newLeadCall.save()
                return Response({"status": 'success',
                'message':'No Lead Found For Mapping',
                'transcript': transcript.text
            }, status=HTTP_200_OK)

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

            try:
                if not send_summary_email(transcript.text, agent.smtp_email, agent.smtp_password, emailModel.email, agent.email_provider):
                    return Response({'Error': f'Email Summary not sent for Lead of id {lead_id}'})
            except Exception as e:
                return Response({'Error': f'Error in sending summary email'})

            async_task(refreshAI, lead_id)
            # try:
            #     # refreshAI(lead_id)
            # except Exception as e:
            #     return Response({'Error': f'Error in refreshing Lead of id {lead_id}'}, status=HTTP_500_INTERNAL_SERVER_ERROR)

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

    
    def get(self, request):
        country = 'US'

        available_numbers = client.available_phone_numbers(
            country).local.list(limit=20)

        return Response({
            'available_numbers': [number.phone_number for number in available_numbers]
        }, status=HTTP_200_OK)

    
    def post(self, request):
        number = request.data.get('number')
        if not number:
            return Response({'error': 'Number is required'}, status=HTTP_400_BAD_REQUEST)
        try:
            purchased_number = client.incoming_phone_numbers.create(
                phone_number=number,
            )
            
            # Update the purchased number to use TwiML app
            purchased_number.update(
                voice_application_sid=twilml_app_sid
            )

            return Response({
                'message': 'Number purchased successfully',
                'purchased_number': purchased_number.phone_number
            }, status=HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)
