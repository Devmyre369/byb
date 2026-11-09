

import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Event(models.Model):

    class EventType(models.TextChoices):
        PERSONAL = "personal", "Personal"
        SOCIAL = "social", "Social"
        PUBLIC = "public", "Public"

    class Visibility(models.TextChoices):
        PRIVATE = "private", "Private"
        SELECTED = "selected", "Selected Audience"
        PUBLIC = "public", "Public"

    class Status(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    class RegistrationMode(models.TextChoices):
        AUTOMATIC = "automatic", "Automatic Confirmation"
        APPROVAL = "approval", "Organiser Approval"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Event ownership
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_events"
    )

    # Basic information
    title = models.CharField(max_length=200)

    description = models.TextField(
        blank=True,
        max_length=5000
    )

    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        db_index=True
    )

    category = models.CharField(
        max_length=80,
        blank=True
    )

    cover_image = models.URLField(
        blank=True,
        max_length=1000
    )

    # Date and time
    starts_at = models.DateTimeField(db_index=True)

    ends_at = models.DateTimeField(
        null=True,
        blank=True
    )

    timezone = models.CharField(
        max_length=64,
        default="UTC"
    )

    # Location
    location_name = models.CharField(
        max_length=200,
        blank=True
    )

    location_address = models.CharField(
        max_length=500,
        blank=True
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        db_index=True
    )

    # Visibility
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True
    )

    # Registration and capacity settings
    capacity = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    registration_enabled = models.BooleanField(default=True)

    registration_mode = models.CharField(
        max_length=20,
        choices=RegistrationMode.choices,
        default=RegistrationMode.AUTOMATIC
    )

    registration_opens_at = models.DateTimeField(
        null=True,
        blank=True
    )

    registration_closes_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Event lifecycle
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPCOMING,
        db_index=True
    )

    # Retention and archival
    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    archive_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True
    )

    archived_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Soft deletion
    is_deleted = models.BooleanField(
        default=False,
        db_index=True
    )

    deleted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deleted_events"
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]

        indexes = [
            models.Index(
                fields=["event_type", "status", "starts_at"],
                name="event_type_status_date_idx"
            ),
            models.Index(
                fields=["visibility", "status", "starts_at"],
                name="event_visibility_date_idx"
            ),
            models.Index(
                fields=["city", "starts_at"],
                name="event_city_date_idx"
            ),
            models.Index(
                fields=["is_deleted", "status"],
                name="event_deleted_status_idx"
            ),
        ]

    def clean(self):
        super().clean()

        if self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({
                "ends_at": "Event end time must be after its start time."
            })

        if (
            self.status == self.Status.ARCHIVED
            and not self.archived_at
        ):
            raise ValidationError({
                "archived_at":
                    "An archived event must have an archive timestamp."
            })

        if self.capacity is not None and self.capacity < 1:
            raise ValidationError({
                "capacity": "Capacity must be at least 1."
            })

        if (
            self.registration_opens_at
            and self.registration_closes_at
            and self.registration_closes_at <= self.registration_opens_at
        ):
            raise ValidationError({
                "registration_closes_at":
                    "Registration closing time must be after opening time."
            })

        if self.is_deleted and not self.deleted_at:
            raise ValidationError({
                "deleted_at":
                    "A deleted event must have a deletion timestamp."
            })

    def __str__(self):
        return f"{self.title} ({self.event_type})"


class EventOrganiser(models.Model):

    class Role(models.TextChoices):
        PRIMARY = "primary", "Primary Organiser"
        CO_ORGANISER = "co_organiser", "Co-organiser"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="organisers"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organised_events"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CO_ORGANISER
    )

    # Organiser permissions
    can_edit_event = models.BooleanField(default=False)
    can_manage_participants = models.BooleanField(default=False)
    can_manage_registrations = models.BooleanField(default=False)
    can_change_visibility = models.BooleanField(default=False)
    can_moderate_media = models.BooleanField(default=False)

    # Only co-organisers need this permission.
    # The event creator always has deletion authority.
    can_delete_event = models.BooleanField(default=False)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["added_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="unique_event_organiser"
            ),
            models.UniqueConstraint(
                fields=["event"],
                condition=models.Q(role="primary"),
                name="one_primary_organiser_per_event"
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.role == self.Role.PRIMARY
            and self.event_id
            and self.user_id
            and self.event.creator_id != self.user_id
        ):
            raise ValidationError({
                "user": "The primary organiser must be the event creator."
            })

        if (
            self.role == self.Role.CO_ORGANISER
            and self.event_id
            and self.user_id
            and self.event.creator_id == self.user_id
        ):
            raise ValidationError({
                "user": "The event creator cannot be added as a co-organiser."
            })

        if (
            self.role == self.Role.PRIMARY
            and self.can_delete_event
        ):
            raise ValidationError({
                "can_delete_event":
                    "The primary organiser does not need an extra deletion permission."
            })

    def __str__(self):
        return f"{self.user} - {self.event.title} ({self.role})"


class EventParticipant(models.Model):

    class Status(models.TextChoices):
        INVITED = "invited", "Invited"
        REQUESTED = "requested", "Requested"
        ACCEPTED = "accepted", "Accepted"
        DECLINED = "declined", "Declined"
        REMOVED = "removed", "Removed"
        LEFT = "Left", "Left"

    class Role(models.TextChoices):
        PARTICIPANT = "participant", "Participant"
        CONTRIBUTOR = "contributor", "Media Contributor"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="participants"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_participations"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.REQUESTED,
        db_index=True
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.PARTICIPANT
    )

    # Media permission
    can_upload_media = models.BooleanField(default=False)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sent_event_invitations"
    )

    joined_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="unique_event_participant"
            )
        ]

        indexes = [
            models.Index(
                fields=["event", "status"],
                name="event_participant_status_idx"
            )
        ]

    def clean(self):
        super().clean()

        if self.event_id and self.user_id:
            if self.event.creator_id == self.user_id:
                raise ValidationError(
                    "The event creator is already the event owner."
                )

            if self.event.event_type == Event.EventType.PUBLIC:
                raise ValidationError(
                    "Public event attendees must use event registration."
                )

    def __str__(self):
        return f"{self.user} - {self.event.title} ({self.status})"


class EventRegistration(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Approval"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_registrations"
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CONFIRMED,
        db_index=True
    )

    registered_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-registered_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="unique_event_registration"
            )
        ]

        indexes = [
            models.Index(
                fields=["event", "status"],
                name="event_registration_status_idx"
            )
        ]

    def clean(self):
        super().clean()

        if self.event_id and self.user_id:
            if self.event.event_type != Event.EventType.PUBLIC:
                raise ValidationError(
                    "Only public events support event registration."
                )

            if self.event.creator_id == self.user_id:
                raise ValidationError(
                    "The event creator cannot register for their own event."
                )

    def __str__(self):
        return f"{self.user} - {self.event.title} ({self.status})"


class EventMedia(models.Model):

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"

    class ModerationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        REMOVED = "removed", "Removed"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="media"
    )

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_event_media"
    )

    # BYB V1 supports images only.
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices,
        default=MediaType.IMAGE
    )

    cloudinary_url = models.URLField(max_length=1000)

    cloudinary_public_id = models.CharField(
        max_length=255,
        unique=True
    )

    caption = models.CharField(max_length=500, blank=True)

    moderation_status = models.CharField(
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.CheckConstraint(
                condition=models.Q(media_type="image"),
                name="event_media_images_only"
            )
        ]

        indexes = [
            models.Index(
                fields=["event", "moderation_status"],
                name="event_media_moderation_idx"
            ),
            models.Index(
                fields=["event", "created_at"],
                name="event_media_created_idx"
            ),
        ]

    def clean(self):
        super().clean()

        if self.media_type != self.MediaType.IMAGE:
            raise ValidationError({
                "media_type": "BYB currently supports image uploads only."
            })

    def __str__(self):
        return f"Image uploaded by {self.uploaded_by}"


class EventComment(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="comments"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="event_comments"
    )

    content = models.TextField(max_length=2000)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )

    is_edited = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

        indexes = [
            models.Index(
                fields=["event", "created_at"],
                name="event_comment_created_idx"
            )
        ]

    def __str__(self):
        return f"Comment by {self.user} on {self.event.title}"


class EventReaction(models.Model):

    class ReactionType(models.TextChoices):
        LIKE = "like", "Like"
        LOVE = "love", "Love"
        CELEBRATE = "celebrate", "Celebrate"
        INTERESTING = "interesting", "Interesting"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="reactions"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="event_reactions"
    )

    reaction_type = models.CharField(
        max_length=20,
        choices=ReactionType.choices,
        default=ReactionType.LIKE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "user"],
                name="unique_event_reaction"
            )
        ]

        indexes = [
            models.Index(
                fields=["event", "reaction_type"],
                name="event_reaction_type_idx"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.reaction_type} - {self.event.title}"
