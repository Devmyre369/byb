
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils.text import slugify

from hubs.models import Hub, HubMembership


@transaction.atomic
def create_hub(*, creator, hub_data):
    """
    Create a Hub and automatically assign its creator
    as its active Owner.
    """

    if not creator or not creator.is_authenticated:
        raise PermissionDenied(
            "You must be logged in to create a Hub."
        )

    data = dict(hub_data)

    # These fields are controlled by the service.
    protected_fields = (
        "id",
        "slug",
        "created_by",
        "verification_status",
        "verified_at",
        "created_at",
        "updated_at",
    )

    for field in protected_fields:
        data.pop(field, None)

    name = data.get("name")

    if not name or not name.strip():
        raise ValidationError(
            "Hub name is required."
        )

    name = name.strip()
    data["name"] = name

    # Generate a unique slug.
    base_slug = slugify(name)

    if not base_slug:
        raise ValidationError(
            "A valid Hub name is required to generate its URL."
        )

    slug = base_slug
    counter = 2

    while Hub.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    hub = Hub(
        created_by=creator,
        slug=slug,
        verification_status=Hub.VerificationStatus.UNVERIFIED,
        **data,
    )

    hub.full_clean()
    hub.save()

    # Automatically create the creator's Owner membership.
    membership = HubMembership(
        hub=hub,
        user=creator,
        role=HubMembership.Role.OWNER,
        status=HubMembership.Status.ACTIVE,
        source=HubMembership.Source.CREATION,
        joined_at=hub.created_at,
    )

    membership.full_clean()
    membership.save()

    return hub


