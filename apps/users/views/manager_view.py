from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *

from apps.users.serializers.manager_serializer import (
    ManagerLoginSerializer,
    ManagerRegisterSerializer
)
from apps.users.permissions import IsAdmin, IsManager
from apps.users.models import ManagerModel, LeadModel
from apps.users.models.agent_model import AgentModel
from apps.aiModule.models import ChatMessageHistory


class ManagerRegisterView(APIView):
    serializer_class = ManagerRegisterSerializer
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ManagerRegisterSerializer(data=request.data)

        if serializer.is_valid():
            manager = serializer.save()
            return Response({'message': 'Manager register successfully'}, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ManagerLoginView(APIView):
    serializer_class = ManagerLoginSerializer

    def post(self, request):
        serializer = ManagerLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)


class ManagerDashboardView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        user = request.user
        manager = ManagerModel.objects.get(user=user)
        agents = AgentModel.objects.filter(assign_manager=manager)
        total_calls = ChatMessageHistory.objects.filter(
            lead__assign_to__in=agents, messageType='call').count()
        total_follow_ups = ChatMessageHistory.objects.filter(
            lead__assign_to__in=agents, wroteBy='ai', follow_up_date__isnull=False).count()
        average_lead_onboard = LeadModel.objects.filter(assign_to__in=agents, status='converted').count(
        ) / LeadModel.objects.filter(assign_to__in=agents).count() * 100

        # Agent with the conversted Lead Number



        return Response({
            'total_calls': total_calls,
            'total_follow_ups': total_follow_ups,
            'average_lead_onboard': average_lead_onboard,
        }, status=HTTP_200_OK)
