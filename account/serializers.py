import datetime
from rest_framework import serializers
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from backend import settings
from .models import IDCard, User



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class IDCardSerializer(serializers.ModelSerializer):
    days_remaining = serializers.SerializerMethodField()
    signature = serializers.SerializerMethodField()
    class Meta:
        model = IDCard
        fields = ["id","id_number","is_active","expired","expired_at","days_remaining",'signature',"first_time"]

    def get_days_remaining(self,obj:IDCard):
        try:
            if obj.expired_at:
                return int((obj.expired_at - datetime.date.today()).days)
            return 0
        except:
            return 0
        
    def get_signature(self, obj):
        if obj.signature:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.signature.url)
            return f"{settings.BASE_URL}{obj.signature.url}"
        return None

    

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    card = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    user_request = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = User 
        fields = ['id', 'email', 'first_name', 'last_name', 'image', 'card','role', 'user_request', 'password', 'created_at', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def get_card(self, obj: User):
        request = self.context.get('request')
        id_card, created = IDCard.objects.get_or_create(user=obj)
        return IDCardSerializer(id_card, context={'request': request}).data

    def get_role(self,obj:User):
        return obj.get_role_display()

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.BASE_URL}{obj.image.url}"
        return None
    
    def get_user_request(self, obj: User):
        """Return user request data if available"""
        if obj.user_request:
            from api.serializers.members import UserRequestSerializer
            return UserRequestSerializer(obj.user_request).data
        return None


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user_id_card, created = IDCard.objects.get_or_create(user=user)
        return user





class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        # Check that new passwords match
        if data['new_password'] != data['confirm_new_password']:
            raise ValidationError("New passwords do not match.")
        return data
    


