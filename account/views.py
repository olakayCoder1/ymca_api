from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from api.utils.response.response_format import success_response, bad_request_response




class LoginUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response = {
                "tokens":{
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                },
                "user": UserSerializer(user,context={'request': request}).data
            }
            return success_response(
                data=response,
                message='User logged in successfully',
            )
        return bad_request_response(
            message='Invalid email or password',
        )




class RegisterUserView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            response = {
                "tokens":{
                    'access_token': access_token,
                    'refresh_token': str(refresh),
                },
                "user": UserSerializer(user,context={'request': request}).data
            }
            return success_response(
                message='User created successfully',
                data=response
            )
        except ValueError as e:
            return bad_request_response(
                message='Invalid request',
            )



class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return success_response(
            data=UserSerializer(request.user,context={'request': request}).data,
        )