
from rest_framework import serializers

from hubs.models import Hub, HubMembership
from hubs.services.hub_service import create_hub


class HubSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(
        source="created_by.username",
        read_only=True,
    )

    member_count = serializers.SerializerMethodField()

    current_membership = serializers.SerializerMethodField()

    class Meta:
        model = Hub

        fields = [
            "id",
            "name",
            "slug",
            "description",
            "hub_type",
            "membership_policy",
            "logo",
            "cover_image",
            "city",
            "location",
            "created_by",
            "created_by_username",
            "verification_status",
            "verified_at",
            "member_count",
            "current_membership",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "slug",
            "created_by",
            "created_by_username",
            "verification_status",
            "verified_at",
            "member_count",
            "current_membership",
            "created_at",
            "updated_at",
        ]

    def get_member_count(self, hub):
        return HubMembership.objects.filter(
            hub=hub,
            status=HubMembership.Status.ACTIVE,
        ).count()

    def get_current_membership(self, hub):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return None

        membership = HubMembership.objects.filter(
            hub=hub,
            user=request.user,
        ).first()

        if membership is None:
            return None

        return {
            "id": str(membership.id),
            "role": membership.role,
            "status": membership.status,
            "source": membership.source,
            "joined_at": membership.joined_at,
        }

    def create(self, validated_data):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required to create a Hub."
            )

        try:
            return create_hub(
                creator=request.user,
                hub_data=validated_data,
            )
        except (ValueError, TypeError) as exc:
            raise serializers.ValidationError(str(exc))

    def update(self, instance, validated_data):
        for field, value in validated_data.items():
            setattr(instance, field, value)

        try:
            instance.full_clean()
            instance.save()
        except Exception as exc:
            from django.core.exceptions import ValidationError

            if isinstance(exc, ValidationError):
                detail = (
                    exc.message_dict
                    if hasattr(exc, "message_dict")
                    else exc.messages
                )
                raise serializers.ValidationError(detail)

            raise

        return instance
