
'''
from rest_framework import serializers

from events.models import EventMedia


class EventMediaSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(read_only=True)
    uploaded_by_id = serializers.ReadOnlyField(source="uploaded_by.pk")

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
        '''

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