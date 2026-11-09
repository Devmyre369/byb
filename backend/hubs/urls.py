
from django.urls import path

from hubs.views import (
    HubListCreateView,
    HubDetailView,
    HubMembershipMeView,
    HubMemberListCreateView,
    HubMembershipRequestListView,
    HubMembershipDetailView,
)


urlpatterns = [
    # Public discovery and Hub details
    path(
        "",
        HubListCreateView.as_view(),
        name="hub-list-create",
    ),
    path(
        "<uuid:hub_id>/",
        HubDetailView.as_view(),
        name="hub-detail",
    ),

    # Current user's membership
    path(
        "<uuid:hub_id>/membership/",
        HubMembershipMeView.as_view(),
        name="hub-membership-me",
    ),

    # Active members and invitations
    path(
        "<uuid:hub_id>/members/",
        HubMemberListCreateView.as_view(),
        name="hub-member-list-create",
    ),

    # Pending join requests
    path(
        "<uuid:hub_id>/requests/",
        HubMembershipRequestListView.as_view(),
        name="hub-membership-requests",
    ),

    # Approve, reject, or remove membership
    path(
        "<uuid:hub_id>/members/<uuid:membership_id>/",
        HubMembershipDetailView.as_view(),
        name="hub-membership-detail",
    ),
]
