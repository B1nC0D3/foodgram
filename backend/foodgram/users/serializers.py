from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from djoser.conf import settings

User = get_user_model()

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
        username = User.objects.get(email=attrs.get('email')).username
        self.user = authenticate(
            username=username, password=attrs.get("password")
        )

        if not self.user:
            self.fail("invalid_credentials")
        return attrs
