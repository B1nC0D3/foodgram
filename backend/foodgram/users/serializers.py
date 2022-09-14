from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from djoser.conf import settings
from djoser.serializers import UserSerializer, UserCreateSerializer


User = get_user_model()

class CustomUserSerializer(UserSerializer):
    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        model = User


class TokenCreateSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, style={"input_type": "password"})

    default_error_messages = {
        "invalid_credentials": settings.CONSTANTS.messages.INVALID_CREDENTIALS_ERROR,
        "inactive_account": settings.CONSTANTS.messages.INACTIVE_ACCOUNT_ERROR,
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
            username=username.username, password=attrs.get("password")
        )

        if not self.user:
            self.fail("invalid_credentials")
        return attrs


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.LOGIN_FIELD,
            settings.USER_ID_FIELD,
            "password",
            'first_name',
            'last_name'
        )
        model = User