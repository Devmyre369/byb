
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


# -------------------------
# USER REGISTRATION
# -------------------------

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=True)
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


# -------------------------
# USER LOGIN
# -------------------------

class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        email = attrs["email"].strip().lower()
        password = attrs["password"]

        user = authenticate(
            request=self.context.get("request"),
            **{
                User.USERNAME_FIELD: email,
                "password": password,
            }
        )

        if not user:
            raise AuthenticationFailed(
                "Invalid email or password."
            )

        if not user.is_verified:
            raise AuthenticationFailed(
                "Please verify your email before logging in."
            )

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "profile_picture": user.profile_picture,
            }
        }


# -------------------------
# PROFILE UPDATE
# -------------------------

class ProfileUpdateSerializer(serializers.ModelSerializer):

    is_profile_complete = serializers.BooleanField(read_only=True)

    class Meta:
        model = User

        fields = [
            "id",
            "email",
            "profile_type",
            "first_name",
            "last_name",
            "username",
            "bio",
            "byb_signature",
            "profile_picture",
            "college",
            "course",
            "academic_year",
            "city",
            "interests",
            "is_profile_complete",
        ]

        read_only_fields = [
            "id",
            "email",
            "profile_picture",
            "is_profile_complete",
        ]

    def validate_profile_type(self, value):

        allowed_types = [
            User.ProfileType.STUDENT,
            User.ProfileType.PROFESSIONAL,
        ]

        if value not in allowed_types:
            raise serializers.ValidationError(
                "Choose either student or professional."
            )

        return value

    def validate_username(self, value):

        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Username cannot be empty."
            )

        return value

    def validate_first_name(self, value):
        return value.strip()

    def validate_last_name(self, value):
        return value.strip()

    def validate_bio(self, value):
        return value.strip()

    def validate_byb_signature(self, value):
        value = value.strip()

        if len(value) > 160:
            raise serializers.ValidationError(
            "BYB Signature cannot exceed 160 characters."
        )

        if value and any(char.isspace() for char in value):
            raise serializers.ValidationError(
            "BYB Signature must be a single word."
        )

        return value

    def validate_college(self, value):
        return value.strip()

    def validate_course(self, value):
        return value.strip()

    def validate_academic_year(self, value):
        return value.strip()

    def validate_city(self, value):
        return value.strip()

    def validate_interests(self, value):

        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Interests must be provided as a list."
            )

        if len(value) > 20:
            raise serializers.ValidationError(
                "You can select a maximum of 20 interests."
            )

        cleaned_interests = []

        for interest in value:

            if not isinstance(interest, str):
                raise serializers.ValidationError(
                    "Every interest must be text."
                )

            interest = interest.strip()

            if not interest:
                continue

            if len(interest) > 40:
                raise serializers.ValidationError(
                    "Each interest must be 40 characters or fewer."
                )

            if interest.casefold() not in [
                item.casefold() for item in cleaned_interests
            ]:
                cleaned_interests.append(interest)

        return cleaned_interests
