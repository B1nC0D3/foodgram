from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from djoser.conf import settings
from djoser.serializers import UserCreateSerializer, UserSerializer
from posts.models import Subscribe
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name', 'is_subscribed')
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscribe.objects.filter(author=obj, follower=user).exists()


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, style={"input_type": "password"})

    default_error_messages = {
        'invalid_credentials': settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        'inactive_account': settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None
        self.fields['email'] = serializers.CharField(required=False)

    def validate(self, attrs):
        if not User.objects.filter(email=attrs.get('email')).exists():
            self.fail('invalid_credentials')
        username = User.objects.get(email=attrs.get('email'))
        self.user = authenticate(
            username=username.username, password=attrs.get('password')
        )

        if not self.user:
            self.fail('invalid_credentials')
        return attrs


class CustomUserCreateSerializer(UserCreateSerializer):
    def create(self, validated_data):
        user = super().create(validated_data)
        group = Group.objects.get(name='user')
        user.groups.add(group)
        admin_group = Group.objects.get(name='admin')
        admin_permissions = admin_group.permissions.all()
        if not admin_permissions.exists():
            admin_group.permissions.set(Permission.objects.all())
        return user

    class Meta:
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            'password',
            'first_name',
            'last_name'
        )
        model = User
