

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import (
    PermissionDenied as DRFPermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import (
    Event,
    EventOrganiser,
    EventParticipant,
    EventRegistration,
)

from events.serializers import EventSerializer

from events.services.access import (
    can_view_event,
    get_accessible_events_queryset,
)

from events.services.event_service import soft_delete_event

from events.services.organiser_service import (
    add_co_organiser,
    update_co_organiser_permissions,
    remove_co_organiser,
)

from events.services.participant_service import (
    request_to_join_event,
    invite_to_event,
    respond_to_invitation,
    approve_join_request,
    decline_join_request,
    leave_event,
    remove_participant,
)

from events.services.registration_service import (
    register_for_event,
    cancel_registration,
    approve_registration,
    reject_registration,
)

from events.services.permissions import (
    can_edit_event,
    can_change_visibility,
    can_manage_participants,
    can_manage_registrations,
)


User = get_user_model()


# --------------------------------------------------
# Shared helpers
# --------------------------------------------------

def handle_service_validation_error(exc):
    detail = (
        exc.message_dict
        if hasattr(exc, "message_dict")
        else exc.messages
    )
    raise DRFValidationError(detail)


def serialize_organiser(organiser):
    return {
        "id": str(organiser.id),
        "user_id": str(organiser.user_id),
        "username": organiser.user.username,
        "role": organiser.role,
        "permissions": {
            "can_edit_event": organiser.can_edit_event,
            "can_manage_participants": organiser.can_manage_participants,
            "can_manage_registrations": organiser.can_manage_registrations,
            "can_change_visibility": organiser.can_change_visibility,
            "can_moderate_media": organiser.can_moderate_media,
            "can_delete_event": organiser.can_delete_event,
        },
        "added_at": organiser.added_at,
    }


def serialize_participant(participant):
    return {
        "id": str(participant.id),
        "user_id": str(participant.user_id),
        "username": participant.user.username,
        "status": participant.status,
        "role": participant.role,
        "can_upload_media": participant.can_upload_media,
        "invited_by_id": (
            str(participant.invited_by_id)
            if participant.invited_by_id
            else None
        ),
        "joined_at": participant.joined_at,
    }


def serialize_registration(registration):
    return {
        "id": str(registration.id),
        "event_id": str(registration.event_id),
        "user_id": str(registration.user_id),
        "username": registration.user.username,
        "status": registration.status,
        "registered_at": registration.registered_at,
        "cancelled_at": registration.cancelled_at,
        "created_at": registration.created_at,
        "updated_at": registration.updated_at,
    }


def get_event_or_404(event_id):
    return get_object_or_404(
        Event,
        pk=event_id,
        is_deleted=False,
    )


# --------------------------------------------------
# Event listing and creation
# --------------------------------------------------

class EventPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class EventListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get(self, request):
        events = (
            get_accessible_events_queryset(request.user)
            .select_related("creator")
            .prefetch_related("organisers")
            .order_by("-created_at")
        )

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(
            events,
            request,
            view=self,
        )

        serializer = EventSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        return Response(
            EventSerializer(
                event,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


# --------------------------------------------------
# Event detail, editing and deletion
# --------------------------------------------------

class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = get_event_or_404(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        return Response(
            EventSerializer(
                event,
                context={"request": request},
            ).data
        )

    def patch(self, request, event_id):
        event = get_event_or_404(event_id)

        if not can_edit_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to edit this event."
            )

        if (
            "visibility" in request.data
            and not can_change_visibility(request.user, event)
        ):
            raise DRFPermissionDenied(
                "You do not have permission to change event visibility."
            )

        serializer = EventSerializer(
            event,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(event, field, value)

        try:
            event.full_clean()
            event.save()
        except ValidationError as exc:
            handle_service_validation_error(exc)

        return Response(
            EventSerializer(
                event,
                context={"request": request},
            ).data
        )

    def delete(self, request, event_id):
        event = get_event_or_404(event_id)

        try:
            soft_delete_event(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        return Response(
            {"detail": "Event deleted successfully."},
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# Event organisers
# --------------------------------------------------

class EventOrganiserListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = get_event_or_404(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        organisers = (
            EventOrganiser.objects
            .filter(event=event)
            .select_related("user")
        )

        return Response([
            serialize_organiser(organiser)
            for organiser in organisers
        ])

    def post(self, request, event_id):
        event = get_event_or_404(event_id)

        user_id = request.data.get("user_id")

        if not user_id:
            raise DRFValidationError({
                "user_id": "This field is required."
            })

        user = get_object_or_404(User, pk=user_id)
        permissions = request.data.get("permissions", {})

        try:
            organiser = add_co_organiser(
                event=event,
                actor=request.user,
                user=user,
                permissions=permissions,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        organiser = (
            EventOrganiser.objects
            .select_related("user")
            .get(pk=organiser.pk)
        )

        return Response(
            serialize_organiser(organiser),
            status=status.HTTP_201_CREATED,
        )


class EventOrganiserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, event_id, organiser_id):
        event = get_event_or_404(event_id)

        try:
            organiser = update_co_organiser_permissions(
                event=event,
                actor=request.user,
                organiser_id=organiser_id,
                permissions=request.data,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        organiser = (
            EventOrganiser.objects
            .select_related("user")
            .get(pk=organiser.pk)
        )

        return Response(serialize_organiser(organiser))

    def delete(self, request, event_id, organiser_id):
        event = get_event_or_404(event_id)

        try:
            remove_co_organiser(
                event=event,
                actor=request.user,
                organiser_id=organiser_id,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        return Response(
            {"detail": "Co-organiser removed successfully."}
        )


# --------------------------------------------------
# Event participants
# --------------------------------------------------

class EventParticipantListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = get_event_or_404(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        participants = (
            EventParticipant.objects
            .filter(event=event)
            .select_related("user", "invited_by")
        )

        if not can_manage_participants(request.user, event):
            participants = participants.filter(
                Q(status=EventParticipant.Status.ACCEPTED)
                | Q(user=request.user)
            )

        return Response([
            serialize_participant(participant)
            for participant in participants
        ])

    def post(self, request, event_id):
        event = get_event_or_404(event_id)

        try:
            user_id = request.data.get("user_id")

            if user_id:
                invited_user = get_object_or_404(User, pk=user_id)

                participant = invite_to_event(
                    event=event,
                    actor=request.user,
                    user=invited_user,
                )
            else:
                participant = request_to_join_event(
                    event=event,
                    user=request.user,
                )

        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        participant = (
            EventParticipant.objects
            .select_related("user", "invited_by")
            .get(pk=participant.pk)
        )

        return Response(
            serialize_participant(participant),
            status=status.HTTP_201_CREATED,
        )


class EventParticipantMeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        event = get_event_or_404(event_id)

        if "accept" not in request.data:
            raise DRFValidationError({
                "accept": "This field is required."
            })

        accept = request.data["accept"]

        if not isinstance(accept, bool):
            raise DRFValidationError({
                "accept": "This field must be true or false."
            })

        try:
            participant = respond_to_invitation(
                event=event,
                user=request.user,
                accept=accept,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        participant = (
            EventParticipant.objects
            .select_related("user", "invited_by")
            .get(pk=participant.pk)
        )

        return Response(serialize_participant(participant))

    def delete(self, request, event_id):
        event = get_event_or_404(event_id)

        try:
            participant = leave_event(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        participant = (
            EventParticipant.objects
            .select_related("user", "invited_by")
            .get(pk=participant.pk)
        )

        return Response({
            "detail": "You have left the event.",
            "participant": serialize_participant(participant),
        })


class EventParticipantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, event_id, participant_id):
        event = get_event_or_404(event_id)
        action = request.data.get("action")

        if action not in ("approve", "decline"):
            raise DRFValidationError({
                "action": "Use either 'approve' or 'decline'."
            })

        try:
            if action == "approve":
                participant = approve_join_request(
                    event=event,
                    actor=request.user,
                    participant_id=participant_id,
                )
            else:
                participant = decline_join_request(
                    event=event,
                    actor=request.user,
                    participant_id=participant_id,
                )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        participant = (
            EventParticipant.objects
            .select_related("user", "invited_by")
            .get(pk=participant.pk)
        )

        return Response(serialize_participant(participant))

    def delete(self, request, event_id, participant_id):
        event = get_event_or_404(event_id)

        try:
            participant = remove_participant(
                event=event,
                actor=request.user,
                participant_id=participant_id,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        participant = (
            EventParticipant.objects
            .select_related("user", "invited_by")
            .get(pk=participant.pk)
        )

        return Response({
            "detail": "Participant removed successfully.",
            "participant": serialize_participant(participant),
        })


# --------------------------------------------------
# Public event registrations
# --------------------------------------------------

class EventRegistrationListCreateView(APIView):
    """
    GET: List registrations (authorised organisers only).
    POST: Register the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        event = get_event_or_404(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        if not can_manage_registrations(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view registrations."
            )

        registrations = (
            EventRegistration.objects
            .filter(event=event)
            .select_related("user")
        )

        return Response([
            serialize_registration(registration)
            for registration in registrations
        ])

    def post(self, request, event_id):
        event = get_event_or_404(event_id)

        try:
            registration = register_for_event(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        registration = (
            EventRegistration.objects
            .select_related("user")
            .get(pk=registration.pk)
        )

        return Response(
            serialize_registration(registration),
            status=status.HTTP_201_CREATED,
        )


class EventRegistrationMeView(APIView):
    """
    DELETE: Cancel the authenticated user's own registration.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, event_id):
        event = get_event_or_404(event_id)

        try:
            registration = cancel_registration(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        registration = (
            EventRegistration.objects
            .select_related("user")
            .get(pk=registration.pk)
        )

        return Response({
            "detail": "Registration cancelled successfully.",
            "registration": serialize_registration(registration),
        })


class EventRegistrationDetailView(APIView):
    """
    PATCH: Approve or reject a pending registration.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, event_id, registration_id):
        event = get_event_or_404(event_id)
        action = request.data.get("action")

        if action not in ("approve", "reject"):
            raise DRFValidationError({
                "action": "Use either 'approve' or 'reject'."
            })

        try:
            if action == "approve":
                registration = approve_registration(
                    event=event,
                    actor=request.user,
                    registration_id=registration_id,
                )
            else:
                registration = reject_registration(
                    event=event,
                    actor=request.user,
                    registration_id=registration_id,
                )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))
        except ValidationError as exc:
            handle_service_validation_error(exc)

        registration = (
            EventRegistration.objects
            .select_related("user")
            .get(pk=registration.pk)
        )

        return Response(serialize_registration(registration))




# --------------------------------------------------
# VibeSpace - Events accepting media uploads
# --------------------------------------------------

class UploadableEventsView(APIView):
    """
    Return events where the authenticated user is authorised
    to upload event media.

    Mirrors can_upload_event_media() permission rules.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        events = (
            Event.objects.filter(
                is_deleted=False,
            )
            .exclude(
                status=Event.Status.ARCHIVED,
            )
            .filter(
                Q(creator=user)
                |
                Q(
                    organisers__user=user,
                    organisers__role=EventOrganiser.Role.CO_ORGANISER,
                    organisers__can_moderate_media=True,
                )
                |
                Q(
                    event_type=Event.EventType.PERSONAL,
                    participants__user=user,
                    participants__status__in=[
                        EventParticipant.Status.INVITED,
                        EventParticipant.Status.ACCEPTED,
                    ],
                    participants__can_upload_media=True,
                )
                |
                Q(
                    event_type=Event.EventType.SOCIAL,
                    participants__user=user,
                    participants__status=EventParticipant.Status.ACCEPTED,
                )
                |
                Q(
                    event_type=Event.EventType.PUBLIC,
                    registrations__user=user,
                    registrations__status=EventRegistration.Status.CONFIRMED,
                )
            )
            .select_related("creator")
            .distinct()
            .order_by("-created_at")
        )

        paginator = EventPagination()
        page = paginator.paginate_queryset(
            events,
            request,
            view=self,
        )

        serializer = EventSerializer(
            page,
            many=True,
            context={"request": request},
        )

        return paginator.get_paginated_response(
            serializer.data
        )
