from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from account.models import User
from api.serializers.bulk_membership import BulkMembershipTypeUpdateSerializer

class BulkMembershipTypeUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = BulkMembershipTypeUpdateSerializer(data=request.data)
        if serializer.is_valid():
            user_ids = serializer.validated_data['user_ids']
            membership_type = serializer.validated_data['membership_type']
            updated = User.objects.filter(id__in=user_ids).update(membership_type=membership_type)
            return Response({
                'success': True,
                'updated_count': updated,
                'membership_type': membership_type
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
