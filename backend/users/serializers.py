from rest_framework import serializers

from .models import CustomUser
from djoser.serializers import UserCreateSerializer


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name', )


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password', )