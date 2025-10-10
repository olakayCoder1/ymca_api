from django.contrib import admin
from .models import SubscriptionPlan, MembershipSubscription, SubscriptionPayment


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_months', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['price']


@admin.register(MembershipSubscription)
class MembershipSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'start_date', 'end_date', 'amount_paid', 'payment_method']
    list_filter = ['status', 'payment_method', 'plan', 'start_date', 'end_date']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'payment_reference']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'activated_at', 'cancelled_at']
    
    fieldsets = (
        ('Subscription Info', {
            'fields': ('user', 'plan', 'status', 'auto_renew')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'activated_at', 'cancelled_at')
        }),
        ('Payment Info', {
            'fields': ('amount_paid', 'payment_method', 'payment_reference')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SubscriptionPayment)
class SubscriptionPaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'subscription', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['payment_reference', 'subscription__user__email']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']