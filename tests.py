from contextlib import contextmanager

from django.db.models.signals import post_save
from django.urls import reverse

from core.tests import BaseDomainTestCase
from faction.models import Faction
from faction.models.leader import LeaderProfile
from user.models import (
    User,
    create_profile as create_profile_signal,
    save_profile as save_profile_signal,
    update_profile_slug as update_profile_slug_signal,
)


@contextmanager
def mute_profile_signals():
    receivers = [
        create_profile_signal,
        save_profile_signal,
        update_profile_slug_signal,
    ]
    for receiver in receivers:
        post_save.disconnect(receiver, sender=User)
    try:
        yield
    finally:
        for receiver in receivers:
            post_save.connect(receiver, sender=User)


class FactionModelTests(BaseDomainTestCase):
    def test_get_root_faction_returns_top_parent(self):
        child = Faction.objects.create(
            name="Eagle Patrol - Bravo",
            organization=self.organization,
            parent=self.faction,
        )

        self.assertEqual(child.get_root_faction(), self.faction)


class LeaderDashboardViewTests(BaseDomainTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.leader_user = cls._create_leader_user()

    @classmethod
    def _create_leader_user(cls):
        with mute_profile_signals():
            user = User.objects.create_user(
                username="leader.dashboard",
                password="testpass123",
                user_type=User.UserType.LEADER,
                first_name="Leader",
                last_name="Dashboard",
            )
        LeaderProfile.objects.create(
            user=user,
            organization=cls.organization,
            faction=cls.faction,
        )
        return user

    def setUp(self):
        self.client.force_login(self.__class__.leader_user)

    def test_dashboard_uses_leader_template(self):
        response = self.client.get(reverse("leaders:dashboard"))
        self.assertTemplateUsed(response, "leader/dashboard.html")

    def test_dashboard_context_includes_quick_actions(self):
        response = self.client.get(reverse("leaders:dashboard"))
        widget_titles = [widget["title"] for widget in response.context["widgets"]]
        self.assertIn("Quick Actions", widget_titles)

    def test_dashboard_context_includes_faction_overview(self):
        response = self.client.get(reverse("leaders:dashboard"))
        widget_titles = [widget["title"] for widget in response.context["widgets"]]
        self.assertIn("Faction Overview", widget_titles)
