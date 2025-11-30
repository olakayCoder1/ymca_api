import uuid
from datetime import date, datetime
from django.db import models
from django.utils import timezone
from account.models import User


class SubscriptionPlan(models.Model):
    """Model for different subscription plans"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_months = models.IntegerField(default=12)  # Duration in months
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['price']


class MembershipSubscription(models.Model):
    """Model for user membership subscriptions with May 31st expiration logic"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    
    # Subscription dates
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Payment information
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Status and metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    auto_renew = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Membership Subscription'
        verbose_name_plural = 'Membership Subscriptions'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.plan.name} ({self.status})"

    def save(self, *args, **kwargs):
        """Override save to implement May 31st expiration logic"""
        if not self.end_date and self.start_date:
            self.end_date = self.calculate_may_31st_expiration(self.start_date)
        
        # Auto-update status based on dates
        if self.status == 'active':
            if self.end_date and self.end_date < date.today():
                self.status = 'expired'
        
        super().save(*args, **kwargs)

    @staticmethod
    def calculate_may_31st_expiration(start_date):
        """
        Calculate expiration date as May 31st of the next year.
        If subscription starts after May 31st, it expires May 31st of the following year.
        If subscription starts before or on May 31st, it expires May 31st of the same year.
        """
        current_year = start_date.year
        may_31st_current_year = date(current_year, 5, 31)
        
        if start_date <= may_31st_current_year:
            # If subscribing before or on May 31st, expires this year's May 31st
            return may_31st_current_year
        else:
            # If subscribing after May 31st, expires next year's May 31st
            return date(current_year + 1, 5, 31)

    def activate(self):
        """Activate the subscription"""
        self.status = 'active'
        self.activated_at = timezone.now()
        self.save()

    def cancel(self):
        """Cancel the subscription"""
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.save()

    def is_active(self):
        """Check if subscription is currently active"""
        return (
            self.status == 'active' and 
            self.start_date <= date.today() <= self.end_date
        )

    def days_until_expiry(self):
        """Calculate days until expiry"""
        if self.end_date:
            delta = self.end_date - date.today()
            return delta.days if delta.days > 0 else 0
        return 0

    def is_expired(self):
        """Check if subscription has expired"""
        return self.end_date and self.end_date < date.today()

    @classmethod
    def get_user_active_subscription(cls, user):
        """Get user's current active subscription"""
        return cls.objects.filter(
            user=user,
            status='active',
            start_date__lte=date.today(),
            end_date__gte=date.today()
        ).first()

    @classmethod
    def get_user_subscription_history(cls, user):
        """Get user's complete subscription history"""
        return cls.objects.filter(user=user).order_by('-created_at')


class SubscriptionPayment(models.Model):
    """Model to track subscription payments"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subscription = models.ForeignKey(MembershipSubscription, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=MembershipSubscription.PAYMENT_METHOD_CHOICES)
    payment_reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Payment gateway response
    gateway_response = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_reference} - {self.amount} ({self.status})"

    def mark_as_paid(self):
        """Mark payment as completed"""
        self.status = 'completed'
        self.paid_at = timezone.now()
        self.save()
        
        # Activate the associated subscription
        if self.subscription.status == 'pending':
            self.subscription.activate()