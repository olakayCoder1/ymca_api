import uuid
from django.db import models

from account.models import User

# Create your models here.


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL , null=True, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField(null=True)
    category = models.CharField(
        max_length=20, 
        default="Announcements",
        choices=(
        ('Announcements','Announcements'),
        ('Events','Events'),
        ('Prayer Requests','Prayer Requests'),
        ('Ministries','Ministries'),
        ('Sermons','Sermons'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)        
    image = models.ImageField(upload_to='post-images')



class UpdateAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post= models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.FileField(upload_to='attachments/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)