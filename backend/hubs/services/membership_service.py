
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from hubs.models import Hub, HubMembership
from hubs.services.permissions import (
    can_approve_members,
    can_invite_members,
    can_remove_members,
)


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _require_authenticated(user):
    if not _is_authenticated(user):
        raise PermissionDenied("Authentication is required.")


def _require_permission(allowed, message):
    if not allowed:
        raise PermissionDenied(message)


def _get_locked_hub(hub):
    return Hub.objects.select_for_update().get(pk=hub.pk)


def _get_locked_membership(hub, membership_id):
    try:
        return HubMembership.objects.select_for_update().get(
            pk=membership_id,
            hub=hub,
        )
    except HubMembership.DoesNotExist:
        raise ValidationError("Membership not found.")


@transaction.atomic
def request_to_join_hub(*, user, hub):
    """Join a Hub or submit a membership request."""

    _require_authenticated(user)
    hub = _get_locked_hub(hub)

    membership = (
        HubMembership.objects.select_for_update()
        .filter(hub=hub, user=user)
        .first()
    )

    if membership and membership.status == HubMembership.Status.ACTIVE:
        return membership

    now = timezone.now()

    if hub.membership_policy == Hub.MembershipPolicy.AUTOMATIC:
        status = HubMembership.Status.ACTIVE
        joined_at = now
    else:
        status = HubMembership.Status.PENDING
        joined_at = None

    if membership:
        membership.role = HubMembership.Role.MEMBER
        membership.status = status
        membership.source = HubMembership.Source.REQUEST
        membership.invited_by = None
        membership.reviewed_by = None
        membership.reviewed_at = None
        membership.joined_at = joined_at
    else:
        membership = HubMembership(
            hub=hub,
            user=user,
            role=HubMembership.Role.MEMBER,
            status=status,
            source=HubMembership.Source.REQUEST,
            joined_at=joined_at,
        )

    membership.full_clean()
    membership.save()

    return membership


@transaction.atomic
def approve_membership_request(*, actor, hub, membership_id):
    """Approve a pending membership request. Owner/Admin only."""

    _require_authenticated(actor)
    hub = _get_locked_hub(hub)

    _require_permission(
        can_approve_members(actor, hub),
        "You do not have permission to approve membership requests.",
    )

    membership = _get_locked_membership(hub, membership_id)

    if membership.status != HubMembership.Status.PENDING:
        raise ValidationError("This membership is not pending.")

    if membership.source != HubMembership.Source.REQUEST:
        raise ValidationError("Only join requests can be approved.")

    now = timezone.now()
    membership.status = HubMembership.Status.ACTIVE
    membership.reviewed_by = actor
    membership.reviewed_at = now
    membership.joined_at = now

    membership.full_clean()
    membership.save()

    return membership


@transaction.atomic
def reject_membership_request(*, actor, hub, membership_id):
    """Reject a pending membership request. Owner/Admin only."""

    _require_authenticated(actor)
    hub = _get_locked_hub(hub)

    _require_permission(
        can_approve_members(actor, hub),
        "You do not have permission to reject membership requests.",
    )

    membership = _get_locked_membership(hub, membership_id)

    if membership.status != HubMembership.Status.PENDING:
        raise ValidationError("This membership is not pending.")

    if membership.source != HubMembership.Source.REQUEST:
        raise ValidationError("Only join requests can be rejected.")

    membership.status = HubMembership.Status.REJECTED
    membership.reviewed_by = actor
    membership.reviewed_at = timezone.now()
    membership.joined_at = None

    membership.full_clean()
    membership.save()

    return membership


@transaction.atomic
def invite_hub_member(*, actor, hub, invited_user):
    """Directly add a user as an active Member. Owner/Admin only."""

    _require_authenticated(actor)
    hub = _get_locked_hub(hub)

    _require_permission(
        can_invite_members(actor, hub),
        "You do not have permission to invite members.",
    )

    if not invited_user or not getattr(invited_user, "pk", None):
        raise ValidationError("A valid user must be provided.")

    if not getattr(invited_user, "is_active", True):
        raise ValidationError("This user account is inactive.")

    if invited_user.pk == actor.pk:
        raise ValidationError("You are already a Hub member.")

    membership = (
        HubMembership.objects.select_for_update()
        .filter(hub=hub, user=invited_user)
        .first()
    )

    if membership and membership.status == HubMembership.Status.ACTIVE:
        raise ValidationError("This user is already an active member.")

    now = timezone.now()

    if membership:
        membership.role = HubMembership.Role.MEMBER
        membership.status = HubMembership.Status.ACTIVE
        membership.source = HubMembership.Source.INVITATION
        membership.invited_by = actor
        membership.reviewed_by = actor
        membership.reviewed_at = now
        membership.joined_at = now
    else:
        membership = HubMembership(
            hub=hub,
            user=invited_user,
            role=HubMembership.Role.MEMBER,
            status=HubMembership.Status.ACTIVE,
            source=HubMembership.Source.INVITATION,
            invited_by=actor,
            reviewed_by=actor,
            reviewed_at=now,
            joined_at=now,
        )

    membership.full_clean()
    membership.save()

    return membership


@transaction.atomic
def remove_hub_member(*, actor, hub, membership_id):
    """Remove a Hub member, respecting the target's role."""

    _require_authenticated(actor)
    hub = _get_locked_hub(hub)

    membership = _get_locked_membership(hub, membership_id)

    _require_permission(
        can_remove_members(actor, hub, membership),
        "You do not have permission to remove this member.",
    )

    if membership.user_id == actor.pk:
        raise ValidationError(
            "Use the leave Hub operation to remove yourself."
        )

    membership.delete()
    return True


@transaction.atomic
def leave_hub(*, user, hub):
    """Allow a user to leave a Hub, subject to ownership protection."""

    _require_authenticated(user)
    hub = _get_locked_hub(hub)

    membership = (
        HubMembership.objects.select_for_update()
        .filter(hub=hub, user=user)
        .first()
    )

    if not membership:
        raise ValidationError("You are not a member of this Hub.")

    if membership.role == HubMembership.Role.OWNER:
        raise ValidationError(
            "The Hub owner cannot leave. Transfer ownership first."
        )

    membership.delete()
    return True
