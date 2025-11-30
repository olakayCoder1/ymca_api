from rest_framework import serializers
from account.models import User

class BulkStatusUpdateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of user IDs to update"
    )
    is_active = serializers.BooleanField(
        help_text="Set to true for Active, false for Inactive"
    )
