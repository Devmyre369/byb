from django.utils import timezone
from rest_framework import serializers

from events.models import Event
from events.services.event_service import create_event


class EventSerializer(serializers.ModelSerializer):
    creator_id = serializers.UUIDField(
        source="creator.id",
        read_only=True,
    )

    class Meta:
        model = Event

        fields = [
            "id",
            "creator_id",
            "title",
            "description",
            "event_type",
            "category",
            "cover_image",
            "starts_at",
            "ends_at",
            "timezone",
            "location_name",
            "location_address",
            "city",
            "visibility",
            "capacity",
            "registration_enabled",
            "registration_mode",
            "registration_opens_at",
            "registration_closes_at",
            "status",
            "completed_at",
            "archive_at",
            "archived_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "creator_id",
            "status",
            "completed_at",
            "archive_at",
            "archived_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        event_type = attrs.get(
            "event_type",
            getattr(self.instance, "event_type", None),
        )

        starts_at = attrs.get(
            "starts_at",
            getattr(self.instance, "starts_at", None),
        )

        ends_at = attrs.get(
            "ends_at",
            getattr(self.instance, "ends_at", None),
        )

        if starts_at and ends_at and ends_at <= starts_at:
            raise serializers.ValidationError({
                "ends_at": "Event end time must be after its start time."
            })

        if (
            event_type == Event.EventType.PUBLIC
            and starts_at
            and starts_at <= timezone.now()
        ):
            raise serializers.ValidationError({
                "starts_at": "Public events must have a future start date and time."
            })

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required to create an event."
            )

        return create_event(
            creator=request.user,
            event_data=validated_data,
        )