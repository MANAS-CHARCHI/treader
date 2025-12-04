from datetime import timedelta, timezone
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
import string
import secrets
# Create your models here.



class User(models.Model):
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
    return timezone.now() + timedelta(hours=24)

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