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
'''


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
