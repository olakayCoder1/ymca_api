from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from account.models import User
from api.serializers.bulk_status import BulkStatusUpdateSerializer

class BulkStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BulkStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            is_active = serializer.validated_data['is_active']
            updated = User.objects.filter(id__in=user_ids).update(is_active=is_active)
            return Response({
                'success': True,
                'updated_count': updated,
                'is_active': is_active
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
