from rest_framework import serializers




class DonationInitiateSerializer(serializers.Serializer):
    """Serializer for initiating a donation"""
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    redirect_url = serializers.CharField(max_length=255)
