
import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q


class Hub(models.Model):

    class HubType(models.TextChoices):
        COLLEGE = "college", "College"
        CLUB = "club", "Club"
        ORGANISATION = "organisation", "Organisation"
        COMMUNITY = "community", "Community"

    class MembershipPolicy(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic"
        APPROVAL = "approval", "Approval Required"

    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    # Basic identity

    name = models.CharField(max_length=150)

    slug = models.SlugField(
        max_length=180,
        unique=True,
    )

    description = models.TextField(
        max_length=2000,
        blank=True,
    )

    hub_type = models.CharField(
        max_length=20,
        choices=HubType.choices,
    )

    # Membership configuration

    membership_policy = models.CharField(
        max_length=20,
        choices=MembershipPolicy.choices,
        default=MembershipPolicy.APPROVAL,
    )

    # Visual identity (Cloudinary URLs)

    logo = models.URLField(
        blank=True,
        null=True,
    )

    cover_image = models.URLField(
        blank=True,
        null=True,
    )

    # Location

    city = models.CharField(
        max_length=100,
        blank=True,
    )

    location = models.CharField(
        max_length=200,
        blank=True,
    )

    # Ownership and verification

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_hubs",
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )

    verified_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # Timestamps

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["hub_type", "city"]),
            models.Index(fields=["verification_status"]),
        ]

    def __str__(self):
        return self.name


class HubMembership(models.Model):

    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        EDITOR = "editor", "Editor"
        MEMBER = "member", "Member"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        REJECTED = "rejected", "Rejected"

    class Source(models.TextChoices):
        CREATION = "creation", "Hub Creation"
        REQUEST = "request", "Join Request"
        INVITATION = "invitation", "Invitation"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    hub = models.ForeignKey(
        Hub,
        on_delete=models.CASCADE,
        related_name="memberships",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hub_memberships",
    )

    # Membership permissions

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.REQUEST,
    )

    # Invitation and approval tracking

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sent_hub_invitations",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviewed_hub_memberships",
    )

    reviewed_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    joined_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    # Timestamps

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["hub", "user"],
                name="unique_hub_membership",
            ),
            models.UniqueConstraint(
                fields=["hub"],
                condition=Q(role="owner"),
                name="one_owner_per_hub",
            ),
        ]

        indexes = [
            models.Index(fields=["hub", "status"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["hub", "role"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.hub} ({self.role})"