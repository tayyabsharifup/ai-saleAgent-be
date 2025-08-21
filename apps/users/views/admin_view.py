from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from apps.users.serializers.admin_serializer import (
    AdminLoginSerializer
)
from apps.users.permissions import IsAdmin
from apps.users.models import AgentModel, ManagerModel


class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)


class ChangeStatusView(APIView):
    permission_classes = [IsAdmin]


    def post(self, request):
        user_id = request.data.get('user_id')
        status = request.data.get('status')

        if not user_id or not status:
            return Response({'message': 'User ID and Status are required'}, status=HTTP_400_BAD_REQUEST)
        # Check if the user_id is of agent or manager

        try:
            if not type(bool(status)) == bool:
                return Response({'message': 'Status should be a boolean value'}, status=HTTP_400_BAD_REQUEST)
            agent = AgentModel.objects.get(id=user_id)
            agent.user.is_active = status
            agent.user.save()
            return Response({'message': 'Status changed successfully'}, status=HTTP_200_OK)
        except AgentModel.DoesNotExist:
            try:
                manager = ManagerModel.objects.get(id=user_id)
                manager.user.is_active = status
                manager.user.save()
                return Response({'message': 'Status changed successfully'}, status=HTTP_200_OK)
            except ManagerModel.DoesNotExist:
                return Response({'message': 'Agent or Manager not found'}, status=HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': 'An error occurred', 'error': str(e)}, status=HTTP_500_INTERNAL_SERVER_ERROR)


