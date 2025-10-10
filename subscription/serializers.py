from rest_framework import serializers
from .models import SubscriptionPlan, MembershipSubscription, SubscriptionPayment


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""
    
    class Meta:
        model = SubscriptionPlan
        fields = [
            'id', 'name', 'description', 'price', 'duration_months',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    """Serializer for subscription payments"""
    
    class Meta:
        model = SubscriptionPayment
        fields = [
            'id', 'amount', 'payment_method', 'payment_reference',
            'status', 'created_at', 'updated_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'paid_at']


class MembershipSubscriptionSerializer(serializers.ModelSerializer):
    """Detailed serializer for membership subscriptions"""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_price = serializers.DecimalField(source='plan.price', max_digits=10, decimal_places=2, read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    payments = SubscriptionPaymentSerializer(many=True, read_only=True)
    is_currently_active = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = MembershipSubscription
        fields = [
            'id', 'user', 'user_name', 'user_email', 'plan', 'plan_name', 'plan_price',
            'start_date', 'end_date', 'amount_paid', 'payment_method', 'payment_reference',
            'status', 'auto_renew', 'notes', 'is_currently_active', 'days_until_expiry',
            'created_at', 'updated_at', 'activated_at', 'cancelled_at', 'payments'
        ]
        read_only_fields = [
            'id', 'user_name', 'user_email', 'plan_name', 'plan_price',
            'is_currently_active', 'days_until_expiry', 'created_at', 
            'updated_at', 'activated_at', 'cancelled_at', 'payments'
        ]

    def get_is_currently_active(self, obj):
        """Check if subscription is currently active"""
        return obj.is_active()

    def get_days_until_expiry(self, obj):
        """Get days until subscription expires"""
        return obj.days_until_expiry()


class MembershipSubscriptionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for subscription lists (for admin user detail page)"""
    
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_currently_active = serializers.SerializerMethodField()
    
    class Meta:
        model = MembershipSubscription
        fields = [
            'id', 'plan_name', 'status', 'status_display', 'start_date', 
            'end_date', 'amount_paid', 'payment_method', 'is_currently_active',
            'created_at'
        ]

    def get_is_currently_active(self, obj):
        """Check if subscription is currently active"""
        return obj.is_active()


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for creating new subscriptions"""
    
    class Meta:
        model = MembershipSubscription
        fields = [
            'user', 'plan', 'start_date', 'amount_paid', 
            'payment_method', 'payment_reference', 'notes'
        ]

    def create(self, validated_data):
        """Create subscription with automatic end_date calculation"""
        subscription = MembershipSubscription(**validated_data)
        # The save method will automatically calculate end_date
        subscription.save()
        return subscription