from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from .models import User, UserActivation
from django.contrib.auth.password_validation import validate_password
import re

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(required=False, allow_blank=True, max_length=150)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'dob', 'gender', 'avatar', 'phone_number', 'is_active', 'created_at', 'updated_at', 'password', 'confirm_password']
        
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'dob': {'required': False},
            'gender': {'required': False},
            'avatar': {'required': False},
            'phone_number': {'required': False},
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data
    
    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        if not username or username.strip() == "":
            email_prefix = email.split('@')[0]
            base_username = re.sub(r'[^a-zA-Z0-9_]', '', email_prefix).lower()
            username_to_try = base_username
            counter = 1
            while User.objects.filter(username=username_to_try).exists():
                username_to_try = f"{base_username}_{counter}"
                counter += 1
            username = username_to_try
            
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password']
        )
        return user
