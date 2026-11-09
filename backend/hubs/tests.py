from django.test import TestCase

# Create your tests here.

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from hubs.models import Hub, HubMembership
from hubs.services.hub_service import create_hub


User = get_user_model()


class HubCreationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com",
            username="hubowner",
            password="TestPassword123!",
        )

        self.hub_data = {
            "name": "Goel Coding Club",
            "hub_type": Hub.HubType.CLUB,
            "description": "A coding community.",
            "city": "Lucknow",
        }

    def test_hub_creation_assigns_creator_as_owner(self):
        hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        membership = HubMembership.objects.get(
            hub=hub,
            user=self.user,
        )

        self.assertEqual(hub.created_by, self.user)
        self.assertEqual(
            membership.role,
            HubMembership.Role.OWNER,
        )
        self.assertEqual(
            membership.status,
            HubMembership.Status.ACTIVE,
        )
        self.assertEqual(
            membership.source,
            HubMembership.Source.CREATION,
        )

    def test_hub_creation_generates_slug(self):
        hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        self.assertEqual(
            hub.slug,
            "goel-coding-club",
        )

    def test_duplicate_hub_names_generate_unique_slugs(self):
        first_hub = create_hub(
            creator=self.user,
            hub_data=self.hub_data,
        )

        second_user = User.objects.create_user(
            email="owner2@example.com",
            username="hubowner2",
            password="TestPassword123!",
        )

        second_hub = create_hub(
            creator=second_user,
            hub_data=self.hub_data,
        )

        self.assertEqual(
            first_hub.slug,
            "goel-coding-club",
        )
        self.assertEqual(
            second_hub.slug,
            "goel-coding-club-2",
        )

    def test_creator_cannot_override_protected_fields(self):
        data = {
            **self.hub_data,
            "slug": "custom-untrusted-slug",
            "verification_status": Hub.VerificationStatus.VERIFIED,
            "created_by": None,
        }

        hub = create_hub(
            creator=self.user,
            hub_data=data,
        )

        self.assertEqual(
            hub.slug,
            "goel-coding-club",
        )
        self.assertEqual(
            hub.verification_status,
            Hub.VerificationStatus.UNVERIFIED,
        )
        self.assertEqual(
            hub.created_by,
            self.user,
        )

    def test_hub_creation_rolls_back_if_owner_creation_fails(self):
        with patch.object(
            HubMembership,
            "save",
            side_effect=RuntimeError("Simulated membership failure"),
        ):
            with self.assertRaises(RuntimeError):
                create_hub(
                    creator=self.user,
                    hub_data=self.hub_data,
                )

        self.assertEqual(Hub.objects.count(), 0)
        self.assertEqual(HubMembership.objects.count(), 0)
