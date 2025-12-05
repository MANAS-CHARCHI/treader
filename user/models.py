from django.utils import timezone
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
import string
import secrets
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import transaction, IntegrityError
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class GenderType(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        NON_BINARY = 'NON_BINARY', _('Non-Binary')
        PREFER_NOT_TO_SAY = 'PREFER_NOT_TO_SAY', _('Prefer not to say')

    id= models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    dob= models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=GenderType.choices,
        default=GenderType.PREFER_NOT_TO_SAY,
        blank=True,
    )
    avatar = models.URLField(blank=True)
    phone_number= models.CharField(max_length=15, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups', # Unique related_name added
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions', # Unique related_name added
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user',
    )

    class Meta:
        db_table = 'User'
        managed = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'


def generate_activation_code():
    length = 32
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def get_expiration_time():
    return timezone.now() + timezone.timedelta(hours=24)

class UserActivation(models.Model):
    id=models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='activation')
    activation_code = models.CharField(max_length=32, unique=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_expiration_time)

    class Meta:
        db_table = 'UserActivation'
        managed = True
        verbose_name = 'User Activation'
        verbose_name_plural = 'User Activations'
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.activation_code:
            for _ in range(10):
                self.activation_code = generate_activation_code()
                try:
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                    return
                except IntegrityError:
                    continue
            raise Exception("Failed to generate a unique activation code after multiple attempts.")
    
        super().save(*args, **kwargs)