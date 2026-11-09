'''

from django.shortcuts import render

# Create your views here.
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from events.models import Event
from events.serializers import EventSerializer
from events.services.access import can_view_event, can_discover_event
from events.services.event_service import soft_delete_event
from events.services.permissions import can_edit_event


class EventListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.filter(
            is_deleted=False
        ).select_related("creator").prefetch_related("organisers")

        accessible_events = [
            event
            for event in events
            if can_view_event(request.user, event)
        ]

        serializer = EventSerializer(
            accessible_events,
            many=True,
            context={"request": request},
        )

        return Response(serializer.data)

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


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_event(self, event_id):
        return get_object_or_404(
            Event.objects.select_related("creator"),
            pk=event_id,
            is_deleted=False,
        )

    def get(self, request, event_id):
        event = self.get_event(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        serializer = EventSerializer(
            event,
            context={"request": request},
        )

        return Response(serializer.data)

    def patch(self, request, event_id):
        event = self.get_event(event_id)

        if not can_edit_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to edit this event."
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
            raise DRFValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)

        return Response(
            EventSerializer(
                event,
                context={"request": request},
            ).data
        )

    def delete(self, request, event_id):
        event = self.get_event(event_id)

        try:
            soft_delete_event(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))

        return Response(
            {"detail": "Event deleted successfully."},
            status=status.HTTP_200_OK,
        )
        


from django.core.exceptions import PermissionDenied, ValidationError
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

from events.models import Event
from events.serializers import EventSerializer
from events.services.access import can_view_event
from events.services.event_service import soft_delete_event
from events.services.permissions import can_edit_event


class EventPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class EventListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get(self, request):
        events = (
            Event.objects
            .filter(is_deleted=False)
            .select_related("creator")
            .prefetch_related("organisers")
            .order_by("-created_at")
        )

        accessible_events = [
            event
            for event in events
            if can_view_event(request.user, event)
        ]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(
            accessible_events,
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


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_event(self, event_id):
        return get_object_or_404(
            Event.objects.select_related("creator"),
            pk=event_id,
            is_deleted=False,
        )

    def get(self, request, event_id):
        event = self.get_event(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        serializer = EventSerializer(
            event,
            context={"request": request},
        )

        return Response(serializer.data)

    def patch(self, request, event_id):
        event = self.get_event(event_id)

        if not can_edit_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to edit this event."
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
            raise DRFValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            )

        return Response(
            EventSerializer(
                event,
                context={"request": request},
            ).data
        )

    def delete(self, request, event_id):
        event = self.get_event(event_id)

        try:
            soft_delete_event(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))

        return Response(
            {"detail": "Event deleted successfully."},
            status=status.HTTP_200_OK,
        )



from django.db.models import Exists, OuterRef, Q

from events.models import (
    Event,
    EventOrganiser,
    EventParticipant,
    EventRegistration,
)


def _is_authenticated(user):
    return bool(
        user
        and getattr(user, "is_authenticated", False)
    )


def _is_event_creator(user, event):
    return (
        _is_authenticated(user)
        and user.pk == event.creator_id
    )


def _is_event_organiser(user, event):
    if not _is_authenticated(user):
        return False

    return EventOrganiser.objects.filter(
        event=event,
        user=user,
    ).exists()


def _is_explicit_participant(user, event):
    if not _is_authenticated(user):
        return False

    participant = EventParticipant.objects.filter(
        event=event,
        user=user,
    ).first()

    if not participant:
        return False

    if event.event_type == Event.EventType.SOCIAL:
        return participant.status == EventParticipant.Status.ACCEPTED

    if event.event_type == Event.EventType.PERSONAL:
        return participant.status in (
            EventParticipant.Status.INVITED,
            EventParticipant.Status.ACCEPTED,
        )

    return False


def _has_confirmed_registration(user, event):
    if not _is_authenticated(user):
        return False

    return EventRegistration.objects.filter(
        event=event,
        user=user,
        status=EventRegistration.Status.CONFIRMED,
    ).exists()


def _has_event_access(user, event):
    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    if event.event_type == Event.EventType.PUBLIC:
        return _has_confirmed_registration(user, event)

    return _is_explicit_participant(user, event)


def can_view_event(user, event):
    """
    Check whether a user can view an event.

    Deleted events are inaccessible.

    Archived events are restricted to the creator,
    organisers, and eligible participants or attendees.

    Before archival:
    - PUBLIC visibility allows authenticated BYB users.
    - SELECTED visibility requires explicit access.
    - PRIVATE visibility requires creator or organiser access.
    """

    if not _is_authenticated(user):
        return False

    if event.is_deleted:
        return False

    if event.status == Event.Status.ARCHIVED:
        return _has_event_access(user, event)

    if _is_event_creator(user, event):
        return True

    if _is_event_organiser(user, event):
        return True

    if event.visibility == Event.Visibility.PUBLIC:
        return True

    if event.visibility == Event.Visibility.SELECTED:
        return _has_event_access(user, event)

    return False


def get_accessible_events_queryset(user):
    """
    Return only events the authenticated user is allowed to view.

    Access rules are applied in SQL using EXISTS subqueries,
    avoiding per-event permission queries in Python.
    """

    if not _is_authenticated(user):
        return Event.objects.none()

    organiser_access = EventOrganiser.objects.filter(
        event_id=OuterRef("pk"),
        user_id=user.pk,
    )

    participant_access = EventParticipant.objects.filter(
        event_id=OuterRef("pk"),
        user_id=user.pk,
    ).filter(
        Q(
            event__event_type=Event.EventType.SOCIAL,
            status=EventParticipant.Status.ACCEPTED,
        )
        | Q(
            event__event_type=Event.EventType.PERSONAL,
            status__in=(
                EventParticipant.Status.INVITED,
                EventParticipant.Status.ACCEPTED,
            ),
        )
    )

    registration_access = EventRegistration.objects.filter(
        event_id=OuterRef("pk"),
        user_id=user.pk,
        status=EventRegistration.Status.CONFIRMED,
    )

    return (
        Event.objects
        .filter(is_deleted=False)
        .annotate(
            _user_is_organiser=Exists(organiser_access),
            _user_is_participant=Exists(participant_access),
            _user_is_registered=Exists(registration_access),
        )
        .filter(
            Q(creator_id=user.pk)
            | Q(_user_is_organiser=True)
            | (
                ~Q(status=Event.Status.ARCHIVED)
                & Q(visibility=Event.Visibility.PUBLIC)
            )
            | (
                Q(status=Event.Status.ARCHIVED)
                & (
                    Q(_user_is_participant=True)
                    | Q(_user_is_registered=True)
                )
            )
            | (
                ~Q(status=Event.Status.ARCHIVED)
                & Q(visibility=Event.Visibility.SELECTED)
                & (
                    Q(_user_is_participant=True)
                    | (
                        Q(event_type=Event.EventType.PUBLIC)
                        & Q(_user_is_registered=True)
                    )
                )
            )
        )
    )


def can_discover_event(user, event):
    """
    Check whether an event can appear in public discovery.
    """

    if not _is_authenticated(user):
        return False

    return (
        not event.is_deleted
        and event.status != Event.Status.ARCHIVED
        and event.visibility == Event.Visibility.PUBLIC
    )



from django.core.exceptions import PermissionDenied, ValidationError
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

from events.models import Event
from events.serializers import EventSerializer
from events.services.access import (
    can_view_event,
    get_accessible_events_queryset,
)
from events.services.event_service import soft_delete_event
from events.services.permissions import can_edit_event


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


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_event(self, event_id):
        return get_object_or_404(
            Event.objects.select_related("creator"),
            pk=event_id,
            is_deleted=False,
        )

    def get(self, request, event_id):
        event = self.get_event(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        serializer = EventSerializer(
            event,
            context={"request": request},
        )

        return Response(serializer.data)

    def patch(self, request, event_id):
        event = self.get_event(event_id)

        if not can_edit_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to edit this event."
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
            raise DRFValidationError(
                exc.message_dict
                if hasattr(exc, "message_dict")
                else exc.messages
            )

        return Response(
            EventSerializer(
                event,
                context={"request": request},
            ).data
        )

    def delete(self, request, event_id):
        event = self.get_event(event_id)

        try:
            soft_delete_event(
                event=event,
                user=request.user,
            )
        except PermissionDenied as exc:
            raise DRFPermissionDenied(str(exc))

        return Response(
            {"detail": "Event deleted successfully."},
            status=status.HTTP_200_OK,
        )



from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
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

from events.models import Event, EventOrganiser
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

from events.services.permissions import (
    can_edit_event,
    can_change_visibility,
)


User = get_user_model()


def handle_service_validation_error(exc):
    """
    Convert Django ValidationError into a DRF ValidationError.
    """
    detail = (
        exc.message_dict
        if hasattr(exc, "message_dict")
        else exc.messages
    )
    raise DRFValidationError(detail)


def serialize_organiser(organiser):
    """
    Return organiser information without exposing unnecessary user data.
    """
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


class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_event(self, event_id):
        return get_object_or_404(
            Event.objects.select_related("creator"),
            pk=event_id,
            is_deleted=False,
        )

    def get(self, request, event_id):
        event = self.get_event(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        serializer = EventSerializer(
            event,
            context={"request": request},
        )

        return Response(serializer.data)

    def patch(self, request, event_id):
        event = self.get_event(event_id)

        if not can_edit_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to edit this event."
            )

        # Visibility changes require a separate permission.
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
        event = self.get_event(event_id)

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


class EventOrganiserListCreateView(APIView):
    """
    GET: List event organisers.
    POST: Add a co-organiser.

    Only the primary organiser can add co-organisers.
    """

    permission_classes = [IsAuthenticated]

    def get_event(self, event_id):
        return get_object_or_404(
            Event,
            pk=event_id,
            is_deleted=False,
        )

    def get(self, request, event_id):
        event = self.get_event(event_id)

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
        event = self.get_event(event_id)

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
    """
    PATCH: Update co-organiser permissions.
    DELETE: Remove a co-organiser.

    Only the primary organiser can perform these actions.
    """

    permission_classes = [IsAuthenticated]

    def get_event(self, event_id):
        return get_object_or_404(
            Event,
            pk=event_id,
            is_deleted=False,
        )

    def patch(self, request, event_id, organiser_id):
        event = self.get_event(event_id)

        permissions = request.data

        try:
            organiser = update_co_organiser_permissions(
                event=event,
                actor=request.user,
                organiser_id=organiser_id,
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

        return Response(serialize_organiser(organiser))

    def delete(self, request, event_id, organiser_id):
        event = self.get_event(event_id)

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
            {"detail": "Co-organiser removed successfully."},
            status=status.HTTP_200_OK,
        )



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

from events.services.permissions import (
    can_edit_event,
    can_change_visibility,
    can_manage_participants,
)


User = get_user_model()


# --------------------------------------------------
# Shared helpers
# --------------------------------------------------

def handle_service_validation_error(exc):
    """
    Convert Django ValidationError into a DRF ValidationError.
    """
    detail = (
        exc.message_dict
        if hasattr(exc, "message_dict")
        else exc.messages
    )
    raise DRFValidationError(detail)


def serialize_organiser(organiser):
    """
    Return organiser information without exposing unnecessary user data.
    """
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
    """
    Return participant information without exposing unnecessary user data.
    """
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

    def get_event(self, event_id):
        return get_event_or_404(event_id)

    def get(self, request, event_id):
        event = self.get_event(event_id)

        if not can_view_event(request.user, event):
            raise DRFPermissionDenied(
                "You do not have permission to view this event."
            )

        serializer = EventSerializer(
            event,
            context={"request": request},
        )

        return Response(serializer.data)

    def patch(self, request, event_id):
        event = self.get_event(event_id)

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
        event = self.get_event(event_id)

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
    """
    GET: List event organisers.
    POST: Add a co-organiser.

    Only the primary organiser can add co-organisers.
    """

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
    """
    PATCH: Update co-organiser permissions.
    DELETE: Remove a co-organiser.

    Only the primary organiser can perform these actions.
    """

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
            {"detail": "Co-organiser removed successfully."},
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# Event participants: listing and invitations
# --------------------------------------------------

class EventParticipantListCreateView(APIView):
    """
    GET: List participants.
    POST: Request to join, or invite a user.

    POST with user_id: Invite that user.
    POST without user_id: Request to join as the authenticated user.
    """

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
                invited_user = get_object_or_404(
                    User,
                    pk=user_id,
                )

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


# --------------------------------------------------
# Event participants: own invitation and leaving
# --------------------------------------------------

class EventParticipantMeView(APIView):
    """
    POST: Accept or decline the authenticated user's invitation.
    DELETE: Leave the Social event.
    """

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

        return Response(
            {
                "detail": "You have left the event.",
                "participant": serialize_participant(participant),
            },
            status=status.HTTP_200_OK,
        )


# --------------------------------------------------
# Event participants: organiser moderation
# --------------------------------------------------

class EventParticipantDetailView(APIView):
    """
    PATCH: Approve or decline a join request.
    DELETE: Remove a participant.

    Only authorised event organisers can perform these actions.
    """

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

        return Response(
            {
                "detail": "Participant removed successfully.",
                "participant": serialize_participant(participant),
            },
            status=status.HTTP_200_OK,
        )
'''


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
