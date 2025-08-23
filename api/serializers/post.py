# posts/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
import base64
import uuid

from api.models import Post, UpdateAttachment
from api.utils.response.response_format import success_response



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class UpdateAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdateAttachment
        fields = ['id', 'file', 'created_at', 'updated_at']


class PostListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    attachments = UpdateAttachmentSerializer(many=True, read_only=True, source='updateattachment_set')

    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'created_at', 'updated_at', 'image', 'attachments']


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    # Base64 file fields for creating/updating
    image_base64 = serializers.CharField(write_only=True, required=False, allow_blank=True)
    image_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    attachments = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    new_attachments = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )
    remove_image = serializers.BooleanField(write_only=True, required=False, default=False)
    
    # Read-only fields for response
    user = UserSerializer(read_only=True)
    attachments_data = UpdateAttachmentSerializer(many=True, read_only=True, source='updateattachment_set')

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'title', 'content', 'created_at', 'updated_at', 'image',
            'image_base64', 'image_name', 'attachments', 'new_attachments', 
            'remove_image', 'attachments_data'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def _decode_base64_file(self, base64_string, filename):
        """Convert base64 string to Django file"""
        try:
            # Handle data URL format (data:image/jpeg;base64,/9j/4AAQ...)
            if ',' in base64_string:
                header, base64_data = base64_string.split(',', 1)
                # Extract file extension from header if available
                if 'image/' in header:
                    ext = header.split('image/')[1].split(';')[0]
                    if not filename.lower().endswith(f'.{ext}'):
                        filename = f"{filename}.{ext}"
            else:
                base64_data = base64_string

            # Decode base64
            file_data = base64.b64decode(base64_data)
            return ContentFile(file_data, name=filename)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 file data: {str(e)}")

    def create(self, validated_data):
        # Extract custom fields
        image_base64 = validated_data.pop('image_base64', None)
        image_name = validated_data.pop('image_name', None)
        attachments_data = validated_data.pop('attachments', [])
        validated_data.pop('new_attachments', None)  # Not used in create
        validated_data.pop('remove_image', None)  # Not used in create

        # Set user from request
        validated_data['user'] = self.context['request'].user

        # Handle image
        if image_base64 and image_name:
            validated_data['image'] = self._decode_base64_file(image_base64, image_name)

        # Create post
        post = Post.objects.create(**validated_data)

        # Handle attachments
        for attachment_data in attachments_data:
            file_base64 = attachment_data.get('file_base64')
            file_name = attachment_data.get('file_name')
            
            if file_base64 and file_name:
                file_obj = self._decode_base64_file(file_base64, file_name)
                UpdateAttachment.objects.create(
                    post=post,
                    file=file_obj
                )

        return post

    def update(self, instance, validated_data):
        # Extract custom fields
        image_base64 = validated_data.pop('image_base64', None)
        image_name = validated_data.pop('image_name', None)
        new_attachments_data = validated_data.pop('new_attachments', [])
        remove_image = validated_data.pop('remove_image', False)
        validated_data.pop('attachments', None)  # Not used in update

        # Handle image removal
        if remove_image:
            if instance.image:
                instance.image.delete(save=False)
            instance.image = None

        # Handle new image
        elif image_base64 and image_name:
            if instance.image:
                instance.image.delete(save=False)
            instance.image = self._decode_base64_file(image_base64, image_name)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()

        # Handle new attachments
        for attachment_data in new_attachments_data:
            file_base64 = attachment_data.get('file_base64')
            file_name = attachment_data.get('file_name')
            
            if file_base64 and file_name:
                file_obj = self._decode_base64_file(file_base64, file_name)
                UpdateAttachment.objects.create(
                    post=instance,
                    file=file_obj
                )

        return instance

    def to_representation(self, instance):
        # Use the list serializer for consistent response format
        return PostListSerializer(instance, context=self.context).data


class AttachmentCreateSerializer(serializers.ModelSerializer):
    file_base64 = serializers.CharField(write_only=True)
    file_name = serializers.CharField(write_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = UpdateAttachment
        fields = ['id', 'post', 'file', 'file_base64', 'file_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'file', 'created_at', 'updated_at']

    def _decode_base64_file(self, base64_string, filename):
        """Convert base64 string to Django file"""
        try:
            if ',' in base64_string:
                header, base64_data = base64_string.split(',', 1)
            else:
                base64_data = base64_string

            file_data = base64.b64decode(base64_data)
            return ContentFile(file_data, name=filename)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid base64 file data: {str(e)}")

    def create(self, validated_data):
        file_base64 = validated_data.pop('file_base64')
        file_name = validated_data.pop('file_name')
        
        validated_data['file'] = self._decode_base64_file(file_base64, file_name)
        
        return super().create(validated_data)