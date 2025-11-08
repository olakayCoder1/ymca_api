from rest_framework import generics
from rest_framework.permissions import AllowAny

from api.models import StaffMember
from api.serializers.staff import StaffMemberSerializer
from api.utils.response.response_format import success_response


class PrincipalOfficersListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffMemberSerializer

    def get_queryset(self):
        return StaffMember.objects.filter(category='principal_officer').order_by('order', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return success_response(data=serializer.data)


class ManagementStaffListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StaffMemberSerializer

    def get_queryset(self):
        return StaffMember.objects.filter(category='management_staff').order_by('order', 'name')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return success_response(data=serializer.data)