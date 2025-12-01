from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import *
from rest_framework.generics import UpdateAPIView, ListAPIView
from rest_framework.permissions import AllowAny
from apps.users.models.lead_model import LeadModel
from apps.users.models.agent_model import AgentModel
from rest_framework.exceptions import ValidationError


from apps.users.serializers.lead_serializer import (
    LeadRegisterSerializer,
    LeadListSerializer,
    LeadDetailSerializer
)
from apps.aiModule.utils.follow_up import refreshAI
from apps.users.permissions import (
    IsAgent,
    IsManager,
    IsAdmin
)

from django_q.tasks import async_task


class LeadRegisterView(APIView):
    serializer_class = LeadRegisterSerializer
    permission_classes = [IsAdmin | IsManager | IsAgent]
    def post(self, request):
        serializer = LeadRegisterSerializer(data = request.data)
        if serializer.is_valid():
            lead = serializer.save()
            try:
                # refreshAI(lead.id)
                async_task(refreshAI, lead.id)
            except Exception as e:
                return Response({'Message': 'User created but failed to add AI message', 'Error': str(e)}, status=HTTP_201_CREATED)
            # send lead_id along with the 
            return Response({'message': f'Lead register successfully with lead id {lead.id}'}, status=HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class LeadUpdateView(UpdateAPIView):
    permission_classes = [IsAgent | IsManager | IsAdmin]
    queryset = LeadModel.objects.all()
    serializer_class = LeadRegisterSerializer
    lookup_field = 'id'

class LeadListView(APIView):
    permission_classes = [IsAgent | IsManager | IsAdmin]
    serializer_class = LeadListSerializer

    def get(self, request):
        leads = LeadModel.objects.prefetch_related('leadphonemodel_set', 'leademailmodel_set').all()
        id = request.query_params.get('id')

        if id:
            if not AgentModel.objects.filter(id=id).exists():
                raise ValidationError(f"Agent with id {id} not found.")
            leads = leads.filter(assign_to=id)
        else:
            leads = leads.filter(assign_to__isnull=True)

        serializer = LeadListSerializer(leads, many=True)
        return Response(serializer.data)
        

class LeadDetailView(APIView):
    permission_classes = [IsAgent]
    serializer_class = LeadDetailSerializer


    def get(self, request):
        lead_id = request.query_params.get('lead_id')
        if not lead_id:
            return Response({'message': 'lead_id query parameter is required.'}, status=HTTP_400_BAD_REQUEST)
        try:
            lead = LeadModel.objects.get(id=lead_id)
        except LeadModel.DoesNotExist:
            return Response({'message': 'Lead not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred', 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = LeadDetailSerializer(lead)
        return Response(serializer.data, status=HTTP_200_OK)