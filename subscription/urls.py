from django.urls import path
from .views import (
    SubscriptionPlanListView,
    UserSubscriptionHistoryView,
    MySubscriptionHistoryView,
    CreateSubscriptionView,
    SubscriptionDetailView,
    ActivateSubscriptionView,
    CancelSubscriptionView,
    UserActiveSubscriptionView
)

urlpatterns = [
    # Subscription plans
    path('plans/', SubscriptionPlanListView.as_view(), name='subscription-plans'),
    
    # Subscription history
    path('user/<uuid:user_id>/history/', UserSubscriptionHistoryView.as_view(), name='user-subscription-history'),
    path('my-history/', MySubscriptionHistoryView.as_view(), name='my-subscription-history'),
    
    # Subscription management
    path('create/', CreateSubscriptionView.as_view(), name='create-subscription'),
    path('<int:pk>/', SubscriptionDetailView.as_view(), name='subscription-detail'),
    path('<int:pk>/activate/', ActivateSubscriptionView.as_view(), name='activate-subscription'),
    path('<int:pk>/cancel/', CancelSubscriptionView.as_view(), name='cancel-subscription'),
    
    # Active subscription
    path('active/', UserActiveSubscriptionView.as_view(), name='my-active-subscription'),
    path('user/<uuid:user_id>/active/', UserActiveSubscriptionView.as_view(), name='user-active-subscription'),
]