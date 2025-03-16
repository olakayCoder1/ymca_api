from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate

from account.models import IDCard, User
from .serializers import LoginSerializer, PasswordChangeSerializer, RegisterSerializer, UserSerializer
from api.utils.response.response_format import success_response, bad_request_response

# 


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
            if not user.is_active:
                return bad_request_response(
                    message="Your account has been deactivated"
                )
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



class PasswordChangeView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        current_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']

        # Check if current password is correct
        if not user.check_password(current_password):
            return bad_request_response(message="Current password is incorrect.")

        # Set new password and save user
        user.set_password(new_password)
        user.save()

        return success_response(message= "Password successfully changed.")
    




class ProfileView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        return success_response(
            data=UserSerializer(request.user,context={'request': request}).data,
        )
    
    def put(self,request):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        gender = request.data.get("gender")
        phone_number = request.data.get("phone_number")

        user:User = request.user

        if first_name:
            user.first_name = first_name

        if last_name:
            user.last_name = last_name


        if gender:
            user.gender = gender

        if phone_number:
            user.phone_number = phone_number


        if email:
            email_exist = User.objects.filter(email=email).exclude(id=request.user.id)
            if email_exist:
                return bad_request_response(
                    message='Email already exist',
                )
            user.email = email
        user.save()

        return success_response(
            data=UserSerializer(request.user,context={'request': request}).data,
            message="Profile updated successfully"
        )
    



class ProfileImageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self,request):
        signature = request.data.get("picture")
        user:User = request.user
        user.image = signature
        user.save()
        return success_response(
            data=UserSerializer(request.user,context={'request': request}).data,
            message="Profile image updated successfully"
        )
    


class CardSignatureView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self,request):
        signature = request.data.get("signature")

        user:User = request.user
        card, created = IDCard.objects.get_or_create(user=user)
        card.signature = signature
        card.save()
        return success_response(
            data=UserSerializer(request.user,context={'request': request}).data,
            message="Signature updated successfully"
        )
    