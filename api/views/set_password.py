from rest_framework import status, generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from account.models import User
from account.serializers import UserSerializer
from api.utils.response.response_format import success_response, bad_request_response

class AdminSetUserPasswordView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id, *args, **kwargs):
        password = request.data.get('password')
        if not password:
            return bad_request_response(message="Password is required.")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return bad_request_response(message="User not found.")
        user.set_password(password)
        user.save()
        return success_response(message="Password updated successfully.")
