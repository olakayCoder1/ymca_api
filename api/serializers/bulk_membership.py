from rest_framework import serializers
from account.models import User

class BulkMembershipTypeUpdateSerializer(serializers.Serializer):
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="List of user IDs to update"
    )
    membership_type = serializers.ChoiceField(
        choices=User.MEMBERSHIP_TYPE_CHOICES,
        help_text="New membership type to set for all users"
    )
