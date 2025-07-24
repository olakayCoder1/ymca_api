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

# # Updated User model with the new fields
# class User(AbstractBaseUser, PermissionsMixin):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     email = models.EmailField(unique=True)
#     first_name = models.CharField(max_length=64, null=True, blank=True)
#     last_name = models.CharField(max_length=64, null=True, blank=True)
#     phone_number = models.CharField(max_length=15, null=True, blank=True)  # Optional
#     gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
#     unit = models.CharField(max_length=64, choices=Unit.choices)
    
#     church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True) 
#     youth_council_group = models.ForeignKey(YouthGroup, on_delete=models.SET_NULL, null=True, blank=True) 


#     is_superuser = models.BooleanField(default=False)
#     is_staff = models.BooleanField(default=False)
#     is_active = models.BooleanField(default=True)
#     is_admin = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     image = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')


#     objects = UserManager()
#     USERNAME_FIELD = "email"

#     def __str__(self):
#         return self.email
    

#     def get_role_display(self):
#         return "Admin" if self.is_admin else "Member"

#     def clean(self):
#         """
#         This method is used to enforce the conditional logic for church name or youth council.
#         """
#         if self.unit == Unit.COUNCIL_OF_CHURCH and not self.church:
#             raise ValueError("Church name is required for Council of Church.")
#         if self.unit == Unit.YOUTH_COUNCIL and not self.youth_council_group:
#             raise ValueError("Youth group (Hi-Y or Y-Elite) is required for Youth Council.")

class MaritalStatus(models.TextChoices):
    SINGLE = 'Single', 'Single'
    MARRIED = 'Married', 'Married'
    DIVORCED = 'Divorced', 'Divorced'
    WIDOWED = 'Widowed', 'Widowed'

class NigerianStates(models.TextChoices):
    ABIA = 'Abia', 'Abia'
    ADAMAWA = 'Adamawa', 'Adamawa'
    AKWA_IBOM = 'Akwa Ibom', 'Akwa Ibom'
    ANAMBRA = 'Anambra', 'Anambra'
    BAUCHI = 'Bauchi', 'Bauchi'
    BAYELSA = 'Bayelsa', 'Bayelsa'
    BENUE = 'Benue', 'Benue'
    BORNO = 'Borno', 'Borno'
    CROSS_RIVER = 'Cross River', 'Cross River'
    DELTA = 'Delta', 'Delta'
    EBONYI = 'Ebonyi', 'Ebonyi'
    EDO = 'Edo', 'Edo'
    EKITI = 'Ekiti', 'Ekiti'
    ENUGU = 'Enugu', 'Enugu'
    GOMBE = 'Gombe', 'Gombe'
    IMO = 'Imo', 'Imo'
    JIGAWA = 'Jigawa', 'Jigawa'
    KADUNA = 'Kaduna', 'Kaduna'
    KANO = 'Kano', 'Kano'
    KATSINA = 'Katsina', 'Katsina'
    KEBBI = 'Kebbi', 'Kebbi'
    KOGI = 'Kogi', 'Kogi'
    KWARA = 'Kwara', 'Kwara'
    LAGOS = 'Lagos', 'Lagos'
    NASARAWA = 'Nasarawa', 'Nasarawa'
    NIGER = 'Niger', 'Niger'
    OGUN = 'Ogun', 'Ogun'
    ONDO = 'Ondo', 'Ondo'
    OSUN = 'Osun', 'Osun'
    OYO = 'Oyo', 'Oyo'
    PLATEAU = 'Plateau', 'Plateau'
    RIVERS = 'Rivers', 'Rivers'
    SOKOTO = 'Sokoto', 'Sokoto'
    TARABA = 'Taraba', 'Taraba'
    YOBE = 'Yobe', 'Yobe'
    ZAMFARA = 'Zamfara', 'Zamfara'
    FCT = 'FCT', 'FCT (Abuja)'

class MembershipCategory(models.TextChoices):
    FULL_MEMBERSHIP = 'Full Membership', 'Full Membership'
    ASSOCIATE_MEMBERSHIP = 'Associate Membership', 'Associate Membership'
    HONORARY_MEMBERSHIP = 'Honorary Membership', 'Honorary Membership'
    STUDENT_MEMBERSHIP = 'Student Membership', 'Student Membership'


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    # Basic Personal Information
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    other_names = models.CharField(max_length=128, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MaritalStatus.choices, null=True, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)
    office_address = models.TextField(null=True, blank=True)
    
    # Background Information
    state_of_origin = models.CharField(max_length=50, choices=NigerianStates.choices, null=True, blank=True)
    nationality = models.CharField(max_length=50, null=True, blank=True)
    profession = models.CharField(max_length=100, null=True, blank=True)
    religion = models.CharField(max_length=50, null=True, blank=True)
    denomination = models.CharField(max_length=100, null=True, blank=True)
    academic_qualification = models.CharField(max_length=200, null=True, blank=True)
    
    # Next of Kin Information
    next_of_kin_name = models.CharField(max_length=128, null=True, blank=True)
    next_of_kin_phone = models.CharField(max_length=15, null=True, blank=True)
    
    # Referral Information
    was_referred = models.BooleanField(default=False)
    referrer_name = models.CharField(max_length=128, null=True, blank=True)
    
    # YMCA Specific Information
    unit = models.CharField(max_length=64, choices=Unit.choices)
    church = models.ForeignKey(Church, on_delete=models.SET_NULL, null=True, blank=True) 
    youth_council_group = models.ForeignKey(YouthGroup, on_delete=models.SET_NULL, null=True, blank=True)


    membership_category = models.CharField(
        max_length=50, 
        choices=MembershipCategory.choices, 
        default=MembershipCategory.FULL_MEMBERSHIP
    )
    
    # Declaration
    declaration_accepted = models.BooleanField(default=False)
    
    # System Fields
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
    
    def get_full_name(self):
        """Return the full name of the user."""
        names = [self.first_name, self.other_names, self.last_name]
        return ' '.join(filter(None, names))
    
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
        
        # Validate declaration for new registrations
        if not self.declaration_accepted:
            raise ValueError("Declaration must be accepted.")
        
        # Validate referrer name if was_referred is True
        if self.was_referred and not self.referrer_name:
            raise ValueError("Referrer name is required when user was referred.")


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
