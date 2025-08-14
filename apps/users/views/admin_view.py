from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import *
from apps.users.serializers.admin_serializer import (
    AdminLoginSerializer
)

class AdminLoginView(APIView):
    serializer_class = AdminLoginSerializer
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)

        if serializer.is_valid():
            return Response(serializer.validated_data, status=HTTP_200_OK)
        else:
            return Response(serializer.errors, status=HTTP_401_UNAUTHORIZED)
