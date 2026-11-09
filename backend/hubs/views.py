from django.shortcuts import render

# Create your views here.

from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import (
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from hubs.models import Hub
from hubs.serializers import HubSerializer
from hubs.services.access import (
    get_discoverable_hubs_queryset,
)
from hubs.services.permissions import (
    can_edit_hub,
)
from django.contrib.auth import get_user_model

from rest_framework.exceptions import ValidationError as DRFValidationError

from hubs.models import HubMembership

from hubs.services.access import (
    get_active_hub_membership,
)

from hubs.services.permissions import (
    can_manage_members,
)

from hubs.services.membership_service import (
    request_to_join_hub,
    leave_hub,
    invite_hub_member,
    approve_membership_request,
    reject_membership_request,
    remove_hub_member,
)

from hubs.services.permissions import (
    can_edit_hub,
    can_manage_members,
)


User = get_user_model()

def handle_service_validation_error(exc):
    detail = (
        exc.message_dict
        if hasattr(exc, "message_dict")
        else exc.messages
    )
    raise DRFValidationError(detail)


def get_hub_or_404(hub_id):
    return get_object_or_404(Hub, pk=hub_id)


class HubPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class HubListCreateView(APIView):
    pagination_class = HubPagination

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def get(self, request):
        hubs = (
            get_discoverable_hubs_queryset()
            .select_related("created_by")
            .order_by("-created_at")
        )

        hub_type = request.query_params.get("hub_type")
        city = request.query_params.get("city")
        search = request.query_params.get("search")

        if hub_type:
            hubs = hubs.filter(hub_type=hub_type)

        if city:
            hubs = hubs.filter(city__iexact=city)

        if search:
            hubs = hubs.filter(
                name__icontains=search
            ) | hubs.filter(
                description__icontains=search
            )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(
            hubs,
            request,
            view=self,
        )

        serializer = HubSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(
            serializer.data
        )

    def post(self, request):
        serializer = HubSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        hub = serializer.save()

        return Response(
            HubSerializer(
                hub,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class HubDetailView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def get(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        return Response(
            HubSerializer(
                hub,
                context={"request": request},
            ).data
        )

    def patch(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        if not can_edit_hub(request.user, hub):
            raise DRFPermissionDenied(
                "Only the Hub Owner or an Admin can edit this Hub."
            )

        serializer = HubSerializer(
            hub,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        try:
            hub = serializer.save()
        except ValidationError as exc:
            handle_service_validation_error(exc)

        return Response(
            HubSerializer(
                hub,
                context={"request": request},
            ).data
        )


# --------------------------------------------------
# Hub membership helpers
# --------------------------------------------------

def serialize_hub_membership(membership):
    return {
        "id": str(membership.id),
        "user_id": str(membership.user_id),
        "username": membership.user.username,
        "role": membership.role,
        "status": membership.status,
        "source": membership.source,
        "invited_by_id": (
            str(membership.invited_by_id)
            if membership.invited_by_id
            else None
        ),
        "reviewed_by_id": (
            str(membership.reviewed_by_id)
            if membership.reviewed_by_id
            else None
        ),
        "reviewed_at": membership.reviewed_at,
        "joined_at": membership.joined_at,
        "created_at": membership.created_at,
    }


def get_membership_or_404(hub, membership_id):
    return get_object_or_404(
        HubMembership.objects.select_related(
            "user",
            "invited_by",
            "reviewed_by",
        ),
        hub=hub,
        pk=membership_id,
    )


# --------------------------------------------------
# Current user's Hub membership
# --------------------------------------------------

class HubMembershipMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        membership = HubMembership.objects.filter(
            hub=hub,
            user=request.user,
        ).select_related(
            "user",
            "invited_by",
            "reviewed_by",
        ).first()

        if membership is None:
            return Response({"membership": None})

        return Response({
            "membership": serialize_hub_membership(membership)
        })

    def post(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        membership = request_to_join_hub(
            user=request.user,
            hub=hub,
        )

        membership = get_membership_or_404(
            hub,
            membership.id,
        )

        return Response({
            "detail": (
                "You are now a Hub member."
                if membership.status == HubMembership.Status.ACTIVE
                else "Your membership request has been submitted."
            ),
            "membership": serialize_hub_membership(membership),
        })

    def delete(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        leave_hub(
            user=request.user,
            hub=hub,
        )

        return Response({
            "detail": "You have left the Hub."
        })


# --------------------------------------------------
# Hub members and invitations
# --------------------------------------------------

class HubMemberListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        return [IsAuthenticated()]

    def get(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        memberships = (
            HubMembership.objects
            .filter(
                hub=hub,
                status=HubMembership.Status.ACTIVE,
            )
            .select_related("user")
            .order_by("joined_at")
        )

        return Response([
            {
                "id": str(membership.id),
                "user_id": str(membership.user_id),
                "username": membership.user.username,
                "role": membership.role,
                "joined_at": membership.joined_at,
            }
            for membership in memberships
        ])

    def post(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        user_id = request.data.get("user_id")

        if not user_id:
            raise DRFValidationError({
                "user_id": "This field is required."
            })

        invited_user = get_object_or_404(
            User,
            pk=user_id,
        )

        membership = invite_hub_member(
            actor=request.user,
            hub=hub,
            invited_user=invited_user,
        )

        membership = get_membership_or_404(
            hub,
            membership.id,
        )

        return Response(
            serialize_hub_membership(membership),
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------
# Pending Hub membership requests
# --------------------------------------------------

class HubMembershipRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, hub_id):
        hub = get_hub_or_404(hub_id)

        if not can_manage_members(request.user, hub):
            raise DRFPermissionDenied(
                "Only Hub Owners and Admins can view membership requests."
            )

        memberships = (
            HubMembership.objects
            .filter(
                hub=hub,
                status=HubMembership.Status.PENDING,
                source=HubMembership.Source.REQUEST,
            )
            .select_related("user")
            .order_by("created_at")
        )

        return Response([
            serialize_hub_membership(membership)
            for membership in memberships
        ])


# --------------------------------------------------
# Approve, reject, or remove a Hub membership
# --------------------------------------------------

class HubMembershipDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, hub_id, membership_id):
        hub = get_hub_or_404(hub_id)

        action = request.data.get("action")

        if action not in ("approve", "reject"):
            raise DRFValidationError({
                "action": "Use either 'approve' or 'reject'."
            })

        if action == "approve":
            membership = approve_membership_request(
                actor=request.user,
                hub=hub,
                membership_id=membership_id,
            )
        else:
            membership = reject_membership_request(
                actor=request.user,
                hub=hub,
                membership_id=membership_id,
            )

        membership = get_membership_or_404(
            hub,
            membership.id,
        )

        return Response(
            serialize_hub_membership(membership)
        )

    def delete(self, request, hub_id, membership_id):
        hub = get_hub_or_404(hub_id)

        remove_hub_member(
            actor=request.user,
            hub=hub,
            membership_id=membership_id,
        )

        return Response({
            "detail": "Hub member removed successfully."
        })
