
from hubs.models import HubMembership

from hubs.services.access import get_active_hub_membership


def _get_active_role(user, hub):
    """Return the user's active role in a Hub, or None."""

    membership = get_active_hub_membership(user, hub)

    if membership is None:
        return None

    return membership.role


def can_edit_hub(user, hub):
    """Only Owners and Admins can edit Hub information."""

    return _get_active_role(user, hub) in {
        HubMembership.Role.OWNER,
        HubMembership.Role.ADMIN,
    }


def can_manage_members(user, hub):
    """Only Owners and Admins can manage Hub membership."""

    return _get_active_role(user, hub) in {
        HubMembership.Role.OWNER,
        HubMembership.Role.ADMIN,
    }


def can_approve_members(user, hub):
    """Only Owners and Admins can approve or reject requests."""

    return can_manage_members(user, hub)


def can_invite_members(user, hub):
    """Only Owners and Admins can invite users."""

    return can_manage_members(user, hub)


def can_remove_members(user, hub, target_membership=None):
    """
    Check whether a user can remove another Hub membership.

    Owners can remove any membership except another Owner.
    Admins can remove Editors and Members, but not Owners or Admins.
    """

    actor_role = _get_active_role(user, hub)

    if actor_role == HubMembership.Role.OWNER:
        if target_membership is None:
            return True

        return target_membership.role != HubMembership.Role.OWNER

    if actor_role == HubMembership.Role.ADMIN:
        if target_membership is None:
            return True

        return target_membership.role in {
            HubMembership.Role.EDITOR,
            HubMembership.Role.MEMBER,
        }

    return False


def can_publish_hub_content(user, hub):
    """Owners, Admins, and Editors can publish Hub content."""

    return _get_active_role(user, hub) in {
        HubMembership.Role.OWNER,
        HubMembership.Role.ADMIN,
        HubMembership.Role.EDITOR,
    }


def can_manage_hub_events(user, hub):
    """Owners, Admins, and Editors can manage Hub events."""

    return can_publish_hub_content(user, hub)


def can_transfer_ownership(user, hub):
    """Only the current Owner can transfer ownership."""

    return _get_active_role(user, hub) == HubMembership.Role.OWNER


def can_delete_hub(user, hub):
    """Only the current Owner can delete a Hub."""

    return _get_active_role(user, hub) == HubMembership.Role.OWNER
