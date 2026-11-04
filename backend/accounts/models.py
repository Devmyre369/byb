
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

    class ProfileType(models.TextChoices):
        STUDENT = "student", "Student"
        PROFESSIONAL = "professional", "Professional"

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

    # Profile type

    profile_type = models.CharField(
        max_length=20,
        choices=ProfileType.choices,
        default=ProfileType.STUDENT
    )

    # Basic profile information

    bio = models.TextField(
        max_length=500,
        blank=True
    )

    # Personal BYB Signature
    # A short statement representing the user's identity.

    byb_signature = models.CharField(
        max_length=160,
        blank=True,
        default=""
    )

    profile_picture = models.URLField(
        blank=True,
        null=True
    )

    # Institution and professional/academic information
    # Students: college, course, academic year
    # Professionals: organization, department/role, experience level

    college = models.CharField(
        max_length=200,
        blank=True
    )

    course = models.CharField(
        max_length=150,
        blank=True
    )

    academic_year = models.CharField(
        max_length=30,
        blank=True
    )

    # Location

    city = models.CharField(
        max_length=100,
        blank=True
    )

    # User interests

    interests = models.JSONField(
        default=list,
        blank=True
    )

    # Account verification

    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    @property
    def is_profile_complete(self):

        required_fields = [
            self.first_name,
            self.username,
            self.college,
            self.course,
            self.academic_year,
            self.city,
        ]

        valid_profile_type = self.profile_type in [
            self.ProfileType.STUDENT,
            self.ProfileType.PROFESSIONAL,
        ]

        return (
            valid_profile_type
            and all(
                field and field.strip()
                for field in required_fields
            )
        )

    def __str__(self):
        return self.username


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
