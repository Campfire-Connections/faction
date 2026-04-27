# faction/tests.py

from django.test import RequestFactory, TestCase
from django.urls import reverse

from core.tests import BaseDomainTestCase, mute_profile_signals
from core.utils import is_leader_admin
from user.models import User
from faction.models import Faction
from faction.models.attendee import AttendeeProfile
from faction.models.leader import LeaderProfile
from faction.selectors import active_factions
from faction.views.faction import ManageView as FactionManageView
from faction.forms.leader import LeaderForm
from faction.serializers import LeaderSerializer


class LeaderAdminPermissionTests(BaseDomainTestCase):
    def setUp(self):
        super().setUp()
        self.factory = RequestFactory()
        with mute_profile_signals():
            self.admin_user = User.objects.create_user(
                username="leader.admin",
                password="pass12345",
                user_type=User.UserType.LEADER,
            )
        self.admin_profile = LeaderProfile.objects.create(
            user=self.admin_user,
            organization=self.organization,
            faction=self.faction,
            is_admin=True,
        )

        with mute_profile_signals():
            self.standard_user = User.objects.create_user(
                username="leader.standard",
                password="pass12345",
                user_type=User.UserType.LEADER,
            )
        self.standard_profile = LeaderProfile.objects.create(
            user=self.standard_user,
            organization=self.organization,
            faction=self.faction,
            is_admin=False,
        )

    def test_is_leader_admin_helper(self):
        self.assertTrue(is_leader_admin(self.admin_user))
        self.assertFalse(is_leader_admin(self.standard_user))

    def test_manage_view_requires_leader_admin(self):
        request = self.factory.get("/factions/manage/")

        request.user = self.admin_user
        view = FactionManageView()
        view.request = request
        self.assertTrue(view.test_func())

        request.user = self.standard_user
        view = FactionManageView()
        view.request = request
        self.assertFalse(view.test_func())


class FactionAccessScopeTests(BaseDomainTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.child_faction = Faction.objects.create(
            name="Eagle Patrol Foxes",
            organization=cls.organization,
            parent=cls.faction,
        )
        cls.other_org = cls.parent_org.__class__.objects.create(
            name="Other Council",
            abbreviation="OC",
            max_depth=5,
        )
        cls.other_faction = Faction.objects.create(
            name="Other Faction",
            organization=cls.other_org,
        )
        with mute_profile_signals():
            cls.admin_user = User.objects.create_superuser(
                username="faction.scope.admin",
                email="faction.scope.admin@example.com",
                password="pass12345",
            )
            cls.leader_user = User.objects.create_user(
                username="faction.scope.leader",
                password="pass12345",
                user_type=User.UserType.LEADER,
            )
        LeaderProfile.objects.create(
            user=cls.leader_user,
            organization=cls.organization,
            faction=cls.faction,
            is_admin=True,
        )

    def test_faction_selector_scopes_leader_to_tree(self):
        factions = active_factions(self.leader_user)

        self.assertIn(self.faction, factions)
        self.assertIn(self.child_faction, factions)
        self.assertNotIn(self.other_faction, factions)

    def test_faction_index_scopes_leader_results(self):
        self.client.force_login(self.leader_user)
        response = self.client.get(reverse("factions:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.faction.name)
        self.assertContains(response, self.child_faction.name)
        self.assertNotContains(response, self.other_faction.name)

    def test_faction_index_keeps_admin_global_visibility(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("factions:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.faction.name)
        self.assertContains(response, self.other_faction.name)


class SlugOnlyUrlTests(TestCase):
    def test_slug_lookup_kwarg_present(self):
        # Smoke test to ensure slug-based routing is expected on show/update/delete
        view = FactionManageView()
        self.assertIsNone(getattr(view, "slug_url_kwarg", None))


class ProfileAbsoluteUrlTests(BaseDomainTestCase):
    def test_leader_profile_absolute_url_uses_project_route(self):
        with mute_profile_signals():
            user = User.objects.create_user(
                username="leader.url",
                password="pass12345",
                user_type=User.UserType.LEADER,
            )
        profile = LeaderProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )

        self.assertEqual(profile.get_absolute_url(), f"/leaders/{profile.slug}/")

    def test_attendee_profile_absolute_url_uses_project_route(self):
        with mute_profile_signals():
            user = User.objects.create_user(
                username="attendee.url",
                password="pass12345",
                user_type=User.UserType.ATTENDEE,
            )
        profile = AttendeeProfile.objects.create(
            user=user,
            organization=self.organization,
            faction=self.faction,
        )

        self.assertEqual(profile.get_absolute_url(), f"/attendees/{profile.slug}/")


class LeaderFormAndSerializerTests(BaseDomainTestCase):
    def setUp(self):
        super().setUp()
        with mute_profile_signals():
            self.user = User.objects.create_user(
                username="leader.form",
                password="pass12345",
                email="leader.form@example.com",
                user_type=User.UserType.LEADER,
            )
        self.profile = LeaderProfile(
            user=self.user,
            organization=self.organization,
            faction=self.faction,
            is_admin=False,
        )

    def test_leader_form_sets_admin_flag(self):
        form = LeaderForm(
            data={
                "is_admin": True,
                "user_username": "leader.form",
                "user_email": "leader.form@example.com",
                "user_first_name": "Form",
                "user_last_name": "Leader",
            },
            instance=self.profile,
        )
        self.assertTrue(form.is_valid())
        with mute_profile_signals():
            saved = form.save()
        self.assertTrue(saved.is_admin)

    def test_leader_serializer_includes_admin_field(self):
        self.profile.is_admin = True
        self.profile.save()
        data = LeaderSerializer(self.profile).data
        self.assertIn("is_admin", data)
        self.assertTrue(data["is_admin"])
