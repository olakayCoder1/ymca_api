
from rest_framework import serializers

from account.models import UserRequest


class UserRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRequest
        fields = [
            'id', 'first_name', 'last_name', 'phone_number', 'address', 
            'valid_id_type', 'valid_id_number', 'passport_photo',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def validate_full_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Full name cannot be empty")
        return value.strip()
    
    def validate_phone_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("Phone number cannot be empty")
        
        # Basic phone number validation
        import re
        phone_pattern = r'^[\+]?[0-9\s\-\(\)]{10,}$'
        if not re.match(phone_pattern, value.strip()):
            raise serializers.ValidationError("Please enter a valid phone number")
        
        return value.strip()
    
    def validate_address(self, value):
        if not value.strip():
            raise serializers.ValidationError("Address cannot be empty")
        return value.strip()
    
    def validate_valid_id_number(self, value):
        if not value.strip():
            raise serializers.ValidationError("Valid ID number cannot be empty")
        return value.strip()
    
    def validate_passport_photo(self, value):
        if not value:
            raise serializers.ValidationError("Passport photo is required")
        
        # Validate file size (max 2MB)
        max_size = 2 * 1024 * 1024  # 2MB
        if value.size > max_size:
            raise serializers.ValidationError("File size must be less than 2MB")
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError("Please upload a valid image file (JPEG, JPG, or PNG)")
        
        return value
    
    def create(self, validated_data):
        # Set the user from the request context
        # validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class UserRequestListSerializer(serializers.ModelSerializer):
    """Serializer for listing requests with full submitted data"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    passport_photo = serializers.ImageField(read_only=True)

    class Meta:
        model = UserRequest
        fields = [
            'id', 'first_name', 'last_name', 'phone_number', 'email',
            'address', 'valid_id_type', 'valid_id_number', 'passport_photo',
            'status', 'status_display', 'created_at'
        ]






