from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "password",
            "password_confirmation",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value):
        return value.strip().lower()

    def validate_username(self, value):
        return value.strip()

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({
                "password_confirmation": "Passwords do not match."
            })

        validate_password(attrs["password"])

        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirmation")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_active=False,
            **validated_data
        )

        return user