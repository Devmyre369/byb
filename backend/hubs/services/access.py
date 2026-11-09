
from django.db.models import QuerySet

from hubs.models import Hub, HubMembership


def _is_authenticated(user):
    """Check whether a user is authenticated."""

    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def get_active_hub_membership(user, hub):
    """
    Return the user's active membership in a Hub.

    Returns None if the user is not an active member.
    """

    if not _is_authenticated(user):
        return None

    return HubMembership.objects.filter(
        hub=hub,
        user=user,
        status=HubMembership.Status.ACTIVE,
    ).first()


def is_active_hub_member(user, hub):
    """Check whether a user is an active Hub member."""

    return get_active_hub_membership(user, hub) is not None


def can_view_hub(user, hub):
    """
    Check whether a Hub can be viewed.

    BYB Hubs are public-only.

    Authentication and membership are not required
    to view a public Hub.
    """

    return hub is not None


def can_discover_hub(user, hub):
    """
    Check whether a Hub can appear in discovery.

    All Hubs are publicly discoverable.
    """

    return hub is not None


def get_discoverable_hubs_queryset() -> QuerySet:
    """
    Return all publicly discoverable Hubs.

    No membership or authentication is required.
    """

    return Hub.objects.all()


def get_user_hubs_queryset(user) -> QuerySet:
    """
    Return Hubs where the user has active membership.

    Pending and rejected memberships are excluded.
    """

    if not _is_authenticated(user):
        return Hub.objects.none()

    return (
        Hub.objects.filter(
            memberships__user=user,
            memberships__status=HubMembership.Status.ACTIVE,
        )
        .distinct()
    )
