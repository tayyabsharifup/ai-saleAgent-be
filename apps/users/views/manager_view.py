from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *

from apps.users.serializers.manager_serializer import (
    ManagerLoginSerializer,
    ManagerRegisterSerializer
)
from apps.users.permissions import IsAdmin

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
        