from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from api.models import StaffMember
from api.serializers.staff import StaffMemberSerializer
from api.utils.response.response_format import success_response
from api.utils.permissions import IsAppAdmin


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


class StaffMemberViewSet(viewsets.ModelViewSet):
    serializer_class = StaffMemberSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = StaffMember.objects.all().order_by('order', 'name')
        category = self.request.query_params.get('category')
        if category in ['principal_officer', 'management_staff']:
            qs = qs.filter(category=category)
        return qs

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAppAdmin()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return success_response(data=serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, context={'request': request})
        return success_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return success_response(message='Staff member created', data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return success_response(message='Staff member updated', data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message='Staff member deleted', data={'id': str(instance.id)})