import secrets
import hashlib

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailOTP


def generate_email_otp(user):

    # Generate a cryptographically secure 6-digit OTP
    otp = f"{secrets.randbelow(1000000):06d}"

    # Hash OTP before storing it
    otp_hash = hashlib.sha256(otp.encode()).hexdigest()

    expires_at = timezone.now() + timedelta(minutes=5)

    # Replace any existing OTP
    EmailOTP.objects.update_or_create(
        user=user,
        defaults={
            "otp_hash": otp_hash,
            "expires_at": expires_at,
            "attempts": 0,
            "is_used": False,
        }
    )

    # Send email
    send_mail(
        subject="Verify your BYB account",
        message=(
            f"Hello {user.username},\n\n"
            f"Your BYB verification OTP is: {otp}\n\n"
            "This OTP expires in 5 minutes.\n\n"
            "If you did not request this, ignore this email."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )