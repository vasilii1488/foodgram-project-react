from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from recipes.models import Follow
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed',)

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            current_user = self.context['request'].user
            return Follow.objects.filter(user=current_user,
                                         following=obj).exists()


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password', )
