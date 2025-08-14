from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.aiModule.models import ChatMessageHistory
from apps.aiModule.serializers import ChatMessageHistorySerializer
from apps.aiModule.utils.follow_up import refreshAI

from apps.users.models.lead_model import LeadModel

# Create your views here.

class chatHistoryView(generics.ListCreateAPIView):
    serializer_class = ChatMessageHistorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        lead_id = self.request.query_params.get('lead_id', None)
        if lead_id is not None:
            return ChatMessageHistory.objects.filter(lead_id=lead_id, wroteBy='ai')
        return ChatMessageHistory.objects.filter(wroteBy='ai')
    
    def perform_create(self, serializer):
        lead_id = self.request.data.get('lead_id', None)
        if lead_id:
            serializer.save(lead_id=lead_id)
        else:
            serializer.save()
    

class chatHistoryAgentView(generics.ListAPIView):
    serializer_class = ChatMessageHistorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        agent_id = self.request.query_params.get('agent_id', None)
        if agent_id is not None:
            return ChatMessageHistory.objects.filter(lead__assign_to=agent_id, wroteBy='ai')

class refreshAIFollowUpView(APIView):
    def get(self, request):
        agent_id = request.query_params.get('id', None)
        if agent_id is not None:
            leads = LeadModel.objects.filter(assign_to=agent_id)
            for lead in leads:
                try:
                    refreshAI(lead.id)
                except:
                    return Response({'Error': f'Error in refreshing Lead of id {lead.id}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'message': f'Agent Lead Refreshed'}, status=status.HTTP_200_OK)
        else:
            return Response({'Error': 'No Agent id provided'}, status=status.HTTP_400_BAD_REQUEST)

