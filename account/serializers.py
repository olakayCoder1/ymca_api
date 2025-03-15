import datetime
from rest_framework import serializers
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from api.serializers.category import ChurchSerializer, YouthGroupSerializer
from backend import settings
from .models import IDCard, User, Church, YouthGroup



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
    church = ChurchSerializer(read_only=True)
    youth_council_group = YouthGroupSerializer(read_only=True)
    card = serializers.SerializerMethodField(read_only=True)
    image = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'gender','image', 'unit', 'church',"card","role",'youth_council_group','password','created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def get_card(self,obj:User):
        request = self.context.get('request')
        id_card , created = IDCard.objects.get_or_create(user=obj)
        return IDCardSerializer(id_card,context={'request': request}).data


    def get_role(self,obj:User):
        return obj.get_role_display()
    

    def get_image(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return f"{settings.BASE_URL}{obj.image.url}"
        return None


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone_number', 'gender', 'unit', 'church', 'youth_council_group','password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            phone_number=validated_data.get('phone_number'),
            gender=validated_data.get('gender'),
            unit=validated_data['unit'],
            church=validated_data.get('church'),
            youth_council_group=validated_data.get('youth_council_group'),
        )
        user_id_card , created = IDCard.objects.get_or_create(user=user)
        return user

    def validate(self, data):
        """
        Validate the user data based on the unit selection.
        This validation ensures that for 'Council of Church', a church name is provided, 
        and for 'Youth Council', a youth group (Hi-Y or Y-Elite) is provided.
        """
        if data['unit'] == 'Council of Church':
            church_name = data.get('church')
            if church_name:
                # Check if the church name exists in the Church model
                try:
                    church = Church.objects.get(id=church_name)
                    data['church'] = church  # If valid, attach the Church object
                except Church.DoesNotExist:
                    raise serializers.ValidationError(f"Church does not exist.")
                    # raise serializers.ValidationError(f"Church with name '{church_name}' does not exist.")
            else:
                raise serializers.ValidationError("Church is required for Council of Church.")
        
        if data['unit'] == 'Youth Council':
            youth_group_name = data.get('youth_council_group')
            if youth_group_name:
                # Check if the youth group name exists in the YouthGroup model
                try:
                    youth_group = YouthGroup.objects.get(name=youth_group_name)
                    data['youth_council_group'] = youth_group  # If valid, attach the YouthGroup object
                except YouthGroup.DoesNotExist:
                    raise serializers.ValidationError(f"Youth group with name '{youth_group_name}' does not exist.")
                    # raise serializers.ValidationError(f"Youth group with name '{youth_group_name}' does not exist.")
            else:
                raise serializers.ValidationError("Youth group (Hi-Y or Y-Elite) is required for Youth Council.")

        return data



class PasswordChangeSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, data):
        # Check that new passwords match
        if data['new_password'] != data['confirm_new_password']:
            raise ValidationError("New passwords do not match.")
        return data
    