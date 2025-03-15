import uuid
from django.db import models

from account.models import User

# Create your models here.


class Transaction(models.Model):
    AVAILABLE_STATUS = (
        ('pending', 'pending'),
        ('success', 'success'),
        ('failed', 'failed'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10)
    response= models.JSONField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10,choices=AVAILABLE_STATUS, default="pending")