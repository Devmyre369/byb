
import uuid
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email address is required")

        if not extra_fields.get("username"):
            raise ValueError("Username is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class User(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    username = models.CharField(
        max_length=30,
        unique=True
    )

    email = models.EmailField(
        unique=True,
        db_index=True
    )

    bio = models.TextField(
        max_length=500,
        blank=True
    )

    profile_picture = models.URLField(
        blank=True,
        null=True
    )

    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class EmailOTP(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_otp"
    )

    otp_hash = models.CharField(max_length=128)

    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    attempts = models.PositiveSmallIntegerField(default=0)

    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"OTP for {self.user.email}"