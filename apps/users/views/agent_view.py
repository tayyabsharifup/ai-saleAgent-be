from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *

from apps.users.serializers.agent_serializer import (
    AgentRegisterSerializer,
    AgentLoginSerializer,
    AgentProfileSerializer,
    AgentDashboardSerializer,
)
from apps.users.serializers.lead_serializer import LeadRegisterSerializer

from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import IsAgent
from apps.users.models import AgentModel

from datetime import date, timedelta

class RegisterAgentView(APIView):
    serializer_class = AgentRegisterSerializer
    def post(self,request):
        serializer = AgentRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message': 'Agent created successfully'}, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class LoginAgentView(APIView):
    serializer_class = AgentLoginSerializer
    def post(self ,request):
        serializer = AgentLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        
        return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)

class AgentProfileView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]
    serializer_class = AgentProfileSerializer
    def get(self, request):
        try:
            agent = AgentModel.objects.get(user=request.user)
            serializer = AgentProfileSerializer(agent)
            return Response(serializer.data, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent profile not found'}, status=HTTP_404_NOT_FOUND)

class AgentDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAgent]
    serializer_class = AgentDashboardSerializer
    def get(self, request):
        try:
            # agent = AgentModel.objects.get(user=request.user)
            # leads = agent.leadmodel_set.all()
            # due_today_num = 0
            # lead_li = []
            # # serializer = AgentProfileSerializer(agent)
            # for lead in leads:
            #     chatMessage = lead.chatmessagehistory_set.all()
            #     # Check if there are any chat messages before accessing the last one
            #     if chatMessage.exists():
            #         due_last_week = chatMessage.last().follow_up_date > date.today() - timedelta(days=7)
            #         if due_last_week:
            #             due_today_num += 1
                
            #     serializer_lead = LeadRegisterSerializer(lead)
            #     lead_li.append(serializer_lead.data)
            # return Response({'total_leads': leads.count(), 'total_messages': due_today_num, 'leads': lead_li})

            agent = AgentModel.objects.get(user=request.user)
            serializer = AgentDashboardSerializer(agent)
            return Response(serializer.data, status=HTTP_200_OK)

        except AgentModel.DoesNotExist:
            return Response({'message': 'Agent not found'}, status=HTTP_404_NOT_FOUND)