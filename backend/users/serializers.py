from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "language_preference", "email_verified", "created_at"]
        read_only_fields = ["id", "email_verified", "created_at"]


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    language_preference = serializers.ChoiceField(
        choices=[("de", "Deutsch"), ("en", "English")], default="en"
    )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["language_preference"]

    def validate_language_preference(self, value):
        valid = [code for code, _ in User.LANGUAGE_CHOICES]
        if value not in valid:
            raise serializers.ValidationError(f"Must be one of: {', '.join(valid)}")
        return value


class MagicLinkRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
