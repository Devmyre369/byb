
import hashlib

from django.db import transaction
from django.utils import timezone
from django.utils.crypto import constant_time_compare

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User, EmailOTP
from .serializers import RegisterSerializer, LoginSerializer
from .utils import generate_email_otp


# -------------------------
# HEALTH CHECK
# -------------------------

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        "status": "success",
        "message": "BYB backend is running!",
        "application": "Beyond Your Bubble",
    })


# -------------------------
# USER REGISTRATION
# -------------------------

class RegisterAPIView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "status": "success",
            "message": "Registration successful. Please verify your email.",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "is_verified": user.is_verified,
            }
        }, status=status.HTTP_201_CREATED)


# -------------------------
# SEND EMAIL OTP
# -------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):

    email = request.data.get("email", "").strip().lower()

    if not email:
        return Response({
            "status": "error",
            "message": "Email is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Account not found."
        }, status=status.HTTP_404_NOT_FOUND)

    if user.is_verified:
        return Response({
            "status": "error",
            "message": "Email is already verified."
        }, status=status.HTTP_400_BAD_REQUEST)

    generate_email_otp(user)

    return Response({
        "status": "success",
        "message": "Verification OTP sent successfully."
    })


# -------------------------
# VERIFY EMAIL OTP
# -------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):

    email = request.data.get("email", "").strip().lower()
    otp = request.data.get("otp", "").strip()

    if not email or not otp:
        return Response({
            "status": "error",
            "message": "Email and OTP are required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        with transaction.atomic():

            user = User.objects.select_for_update().get(email=email)
            otp_record = EmailOTP.objects.select_for_update().get(user=user)

            if user.is_verified:
                return Response({
                    "status": "success",
                    "message": "Email is already verified."
                })

            if otp_record.is_used:
                return Response({
                    "status": "error",
                    "message": "OTP is invalid or already used."
                }, status=status.HTTP_400_BAD_REQUEST)

            if otp_record.expires_at <= timezone.now():
                otp_record.is_used = True
                otp_record.save(update_fields=["is_used"])

                return Response({
                    "status": "error",
                    "message": "OTP has expired. Request a new one."
                }, status=status.HTTP_400_BAD_REQUEST)

            if otp_record.attempts >= 5:
                otp_record.is_used = True
                otp_record.save(update_fields=["is_used"])

                return Response({
                    "status": "error",
                    "message": "Maximum verification attempts exceeded."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)

            submitted_hash = hashlib.sha256(otp.encode()).hexdigest()

            if not constant_time_compare(
                submitted_hash,
                otp_record.otp_hash
            ):
                otp_record.attempts += 1

                if otp_record.attempts >= 5:
                    otp_record.is_used = True

                otp_record.save(
                    update_fields=["attempts", "is_used"]
                )

                return Response({
                    "status": "error",
                    "message": "Invalid OTP."
                }, status=status.HTTP_400_BAD_REQUEST)

            otp_record.is_used = True
            otp_record.save(update_fields=["is_used"])

            user.is_verified = True
            user.is_active = True
            user.save(update_fields=["is_verified", "is_active"])

        return Response({
            "status": "success",
            "message": "Email verified successfully. Your BYB account is now active."
        })

    except User.DoesNotExist:
        return Response({
            "status": "error",
            "message": "Account not found."
        }, status=status.HTTP_404_NOT_FOUND)

    except EmailOTP.DoesNotExist:
        return Response({
            "status": "error",
            "message": "No OTP found. Request a new OTP."
        }, status=status.HTTP_404_NOT_FOUND)


# -------------------------
# USER LOGIN
# -------------------------

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):

    serializer = LoginSerializer(
        data=request.data,
        context={"request": request}
    )

    serializer.is_valid(raise_exception=True)

    return Response({
        "status": "success",
        "message": "Login successful.",
        **serializer.validated_data
    })


# -------------------------
# USER LOGOUT
# -------------------------

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):

    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response({
            "status": "error",
            "message": "Refresh token is required."
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)

        if str(token["user_id"]) != str(request.user.id):
            return Response({
                "status": "error",
                "message": "Invalid refresh token."
            }, status=status.HTTP_403_FORBIDDEN)

        token.blacklist()

        return Response({
            "status": "success",
            "message": "Logged out successfully."
        })

    except TokenError:
        return Response({
            "status": "error",
            "message": "Invalid or expired refresh token."
        }, status=status.HTTP_400_BAD_REQUEST)


# -------------------------
# CURRENT USER PROFILE
# -------------------------


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def current_user(request):

    user = request.user

    if request.method == "PATCH":

        from .serializers import ProfileUpdateSerializer

        serializer = ProfileUpdateSerializer(
            user,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "status": "success",
            "message": "Profile updated successfully.",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "bio": user.bio,
                "profile_picture": user.profile_picture,
                "is_verified": user.is_verified,
            }
        })

    return Response({
        "status": "success",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "bio": user.bio,
            "profile_picture": user.profile_picture,
            "is_verified": user.is_verified,
        }
    })


# -------------------------
# JWT TOKEN REFRESH
# -------------------------

class BYBTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]
