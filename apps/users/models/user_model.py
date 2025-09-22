from django.db import models
from django.contrib.auth.models import UserManager, AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
import random

# Create your models here.

class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("No email provided")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)
        
class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(blank=True, default="", unique=True)
    first_name = models.CharField(max_length=225, blank=True, default="")
    last_name = models.CharField(max_length=225, blank=True, default='')

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now=True)

    role = models.CharField(
        max_length=10, 
        choices=[('admin', 'admin'), ('manager', 'manager'), ('agent', 'agent')],
        default='agent'
    )

    # phone_number = models.CharField(max_length=20,  blank=True, default='')

    otp = models.CharField(max_length=5, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=True) # DEFAULT SHOULD BE FALSE
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

    def generate_otp(self):
        self.otp = str(random.randint(10_000, 99_999))
        self.otp_created_at = timezone.now()

        self.save()


        subject = "Please Verify this OTP code"
        message = f"Thank you for verification. Your OTP code is {self.otp}"
        from_email = settings.EMAIL_HOST_USER
        recipient = [self.email]

        if settings.DEBUG:
            print(f"OTP for {self.email}: {self.otp}")
            return True

        response = send_mail(subject, message, from_email, recipient)
        if str(response) == '1':
            return True
        else:
            return False
    
    def verify_otp(self, otp):
        if settings.DEBUG:
            if otp == '12345':
                self.is_verified = True
                self.save()
                return True
        if self.otp and self.otp_created_at:
            time = (timezone.now() - self.otp_created_at).total_seconds()

            if time < 300 and self.otp == str(otp):
                self.is_verified = True
                self.save()
                return True
        
        return False