from rest_framework import serializers
from recipes.models import Follow
from .models import CustomUser
from djoser.serializers import UserCreateSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)
    
    def get_is_subscribed(self, obj):
        return Follow.objects.filter(following=obj).exists()



class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password', )