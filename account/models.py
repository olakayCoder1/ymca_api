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
    
    # Essential Personal Information for Authentication
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    
    # Reference to UserRequest for detailed information
    user_request = models.OneToOneField('UserRequest', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_user')
    
    # System Fields
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Profile image
    image = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')

    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name of the user."""
        if self.user_request:
            # Get full name from UserRequest if available
            names = [self.user_request.first_name, self.user_request.last_name]
            return ' '.join(filter(None, names))
        else:
            # Fallback to User model fields
            names = [self.first_name, self.last_name]
            return ' '.join(filter(None, names))
    
    def get_role_display(self):
        return "Admin" if self.is_admin else "Member"
    
    def get_detailed_info(self):
        """Return detailed information from UserRequest if available."""
        return self.user_request if self.user_request else None


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



class ValidIdType(models.TextChoices):
    NIN = 'national_id', 'National Identity Number (NIN)'
    DRIVERS_LICENSE = 'drivers_license', 'Driver\'s License'
    VOTERS_CARD = 'voters_card', 'Voter\'s Card'
    INTERNATIONAL_PASSPORT = 'international_passport', 'International Passport'
    BVN = 'bvn', 'Bank Verification Number (BVN)'

class RequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    IN_REVIEW = 'in_review', 'In Review'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'
    COMPLETED = 'completed', 'Completed'

class UserRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,blank=True, related_name='requests')
    
    email = models.EmailField(null=True,blank=True)
    # Personal Information from form
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    
    # Location Information
    citizen = models.CharField(max_length=20, default='Nigerian')  # Nigerian or Foreigner
    country = models.CharField(max_length=100,null=True, blank=True)
    state = models.CharField(max_length=100,null=True, blank=True)
    lga = models.CharField(max_length=100, null=True, blank=True)  # Only for Nigerians
    
    # YMCA Information
    unit = models.CharField(max_length=100,null=True, blank=True)
    club = models.CharField(max_length=100, null=True, blank=True)
    
    # Additional Personal Information
    age = models.CharField(max_length=10, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)
    office_address = models.TextField(null=True, blank=True)
    profession = models.CharField(max_length=200, null=True, blank=True)
    religion = models.CharField(max_length=100, null=True, blank=True)
    church_name = models.CharField(max_length=200, null=True, blank=True)
    occupation = models.CharField(max_length=200, null=True, blank=True)
    marital_status = models.CharField(max_length=50, null=True, blank=True)
    
    # ID Information
    # valid_id_type = models.CharField(max_length=50, choices=ValidIdType.choices)
    valid_id_number = models.CharField(max_length=100, null=True, blank=True)
    
    # File Uploads
    passport_photo = models.ImageField(upload_to='request_photos/')
    valid_id_file = models.ImageField(upload_to='request_photos/', null=True, blank=True)
    
    # Referral Information
    next_of_kin = models.CharField(max_length=255, null=True, blank=True)
    referral_source = models.CharField(max_length=255, null=True, blank=True)
    referral_name = models.CharField(max_length=255, null=True, blank=True)
    referred_by = models.CharField(max_length=10, default='no')  # yes or no
    
    # Legacy field for backward compatibility
    address = models.TextField(null=True, blank=True)
    
    # Request Management
    status = models.CharField(
        max_length=20, 
        choices=RequestStatus.choices, 
        default=RequestStatus.PENDING
    )
    
    # Admin fields
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviewed_requests'
    )
    review_notes = models.TextField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Request'
        verbose_name_plural = 'User Requests'
    
    def __str__(self):
        return f"Request by {self.first_name} - {self.status}"
    
    def clean(self):
        """Validate the request data"""
        super().clean()
        
        if not self.first_name.strip():
            raise ValueError("Full name is required")
        
        if not self.last_name.strip():
            raise ValueError("Full name is required")
        
        if not self.phone_number.strip():
            raise ValueError("Phone number is required")
        
        if not self.address.strip():
            raise ValueError("Address is required")
        
        if not self.valid_id_number.strip():
            raise ValueError("Valid ID number is required")


# serializers.py
