from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from account.models import User
from .models import SubscriptionPlan, MembershipSubscription, SubscriptionPayment
from .serializers import (
    SubscriptionPlanSerializer, 
    MembershipSubscriptionSerializer,
    MembershipSubscriptionListSerializer,
    CreateSubscriptionSerializer
)
from api.utils.response.response_format import success_response, paginate_success_response, bad_request_response


class SubscriptionPlanListView(generics.ListAPIView):
    """List all available subscription plans"""
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsAuthenticated]
    queryset = SubscriptionPlan.objects.filter(is_active=True)


class UserSubscriptionHistoryView(generics.ListAPIView):
    """Get subscription history for a specific user (for admin)"""
    serializer_class = MembershipSubscriptionListSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, id=user_id)
        return MembershipSubscription.objects.filter(user=user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class MySubscriptionHistoryView(generics.ListAPIView):
    """Get subscription history for the authenticated user"""
    serializer_class = MembershipSubscriptionListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return MembershipSubscription.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class CreateSubscriptionView(generics.CreateAPIView):
    """Create a new subscription (admin only)"""
    serializer_class = CreateSubscriptionSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        
        # Return detailed subscription data
        response_serializer = MembershipSubscriptionSerializer(subscription)
        return success_response(
            data=response_serializer.data,
            message="Subscription created successfully"
        )


class SubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a subscription (admin only)"""
    serializer_class = MembershipSubscriptionSerializer
    permission_classes = [IsAdminUser]
    queryset = MembershipSubscription.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        
        return success_response(
            data=serializer.data,
            message="Subscription updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="Subscription deleted successfully")


class ActivateSubscriptionView(generics.GenericAPIView):
    """Activate a subscription (admin only)"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        subscription = get_object_or_404(MembershipSubscription, pk=pk)
        subscription.activate()
        
        serializer = MembershipSubscriptionSerializer(subscription)
        return success_response(
            data=serializer.data,
            message="Subscription activated successfully"
        )


class CancelSubscriptionView(generics.GenericAPIView):
    """Cancel a subscription (admin only)"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        subscription = get_object_or_404(MembershipSubscription, pk=pk)
        subscription.cancel()
        
        serializer = MembershipSubscriptionSerializer(subscription)
        return success_response(
            data=serializer.data,
            message="Subscription cancelled successfully"
        )


class UserActiveSubscriptionView(generics.GenericAPIView):
    """Get user's current active subscription"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        if user_id and request.user.is_admin:
            # Admin can check any user's active subscription
            user = get_object_or_404(User, id=user_id)
        else:
            # Regular users can only check their own
            user = request.user

        active_subscription = MembershipSubscription.get_user_active_subscription(user)
        
        if active_subscription:
            serializer = MembershipSubscriptionSerializer(active_subscription)
            return success_response(data=serializer.data)
        else:
            return success_response(
                data=None,
                message="No active subscription found"
            )