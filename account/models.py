import random, uuid
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

# Choices for Gender and Unit
class Gender(models.TextChoices):
    MALE = 'Male', _('Male')
    FEMALE = 'Female', _('Female')
    OTHER = 'Other', _('Other')

class Unit(models.TextChoices):
    COUNCIL_OF_CHURCH = 'Council of Church', _('Council of Church')
    YOUTH_COUNCIL = 'Youth Council', _('Youth Council')
    YS_MEN = "Y's Men", _("Y's Men")
    CENTRAL_CLUB = 'Central Club', _('Central Club')

# Category model for other parts of your application
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class Church(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name



class YouthGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

# UserManager remains the same
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('superuser must be given is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('superuser must be given is_superuser=True')
        return self.create_user(email, password, **extra_fields)

# Updated User model with the new fields
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # Optional
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    unit = models.CharField(max_length=64, choices=Unit.choices)
    
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True) 
    youth_council_group = models.ForeignKey(YouthGroup, on_delete=models.SET_NULL, null=True, blank=True) 


    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    image = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')


    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    

    def get_role_display(self):
        return "Admin" if self.is_admin else "Member"

    def clean(self):
        """
        This method is used to enforce the conditional logic for church name or youth council.
        """
        if self.unit == Unit.COUNCIL_OF_CHURCH and not self.church:
            raise ValueError("Church name is required for Council of Church.")
        if self.unit == Unit.YOUTH_COUNCIL and not self.youth_council_group:
            raise ValueError("Youth group (Hi-Y or Y-Elite) is required for Youth Council.")


class IDCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_number = models.CharField(max_length=64)
    first_time = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    expired = models.BooleanField(default=True)
    signature = models.ImageField(upload_to='signatures/', null=True , blank=True)
    expired_at = models.DateField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    # add a function to auto generate id_number
    def save(self, *args, **kwargs):
        if not self.id_number:
            self.id_number = 'NTST{}'.format(str(random.randint(123456789000, 9876543210000)))
        super().save(*args, **kwargs)
