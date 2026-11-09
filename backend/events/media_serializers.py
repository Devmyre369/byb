
from rest_framework import serializers

from events.models import EventMedia


class EventMediaSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(read_only=True)

    uploaded_by_id = serializers.UUIDField(
        source="uploaded_by.pk",
        read_only=True,
    )

    class Meta:
        model = EventMedia
        fields = [
            "id",
            "event_id",
            "uploaded_by_id",
            "media_type",
            "cloudinary_url",
            "caption",
            "moderation_status",
            "created_at",
        ]
        read_only_fields = fields


class MomentFeedSerializer(serializers.ModelSerializer):
    uploader = serializers.SerializerMethodField()
    event = serializers.SerializerMethodField()

    class Meta:
        model = EventMedia
        fields = [
            "id",
            "media_type",
            "cloudinary_url",
            "caption",
            "created_at",
            "uploader",
            "event",
        ]
        read_only_fields = fields

    def get_uploader(self, obj):
        user = obj.uploaded_by

        return {
            "id": str(user.pk),
            "username": user.username,
            "first_name": user.first_name,
            "profile_picture": user.profile_picture or "",
        }

    def get_event(self, obj):
        event = obj.event

        return {
            "id": str(event.pk),
            "title": event.title,
            "location_name": event.location_name,
            "city": event.city,
        }
