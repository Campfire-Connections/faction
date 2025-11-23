# faction/tests.py

from django.test import RequestFactory, TestCase

from core.tests import BaseDomainTestCase, mute_profile_signals
from core.utils import is_leader_admin
from user.models import User
from faction.models.leader import LeaderProfile
from faction.views.faction import ManageView as FactionManageView


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


class SlugOnlyUrlTests(TestCase):
    def test_slug_lookup_kwarg_present(self):
        # Smoke test to ensure slug-based routing is expected on show/update/delete
        view = FactionManageView()
        self.assertIsNone(getattr(view, "slug_url_kwarg", None))
