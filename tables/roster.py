# faction/tables/roster.py
import django_tables2 as tables
from django.urls import reverse

from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from faction.models.leader import LeaderProfile
from faction.models.attendee import AttendeeProfile


class RosterTable(ActionsColumnMixin, ActionUrlMixin, tables.Table):
    username = tables.Column(accessor="user.username", verbose_name="Username")
    first_name = tables.Column(accessor="user.first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="user.last_name", verbose_name="Last Name")
    email = tables.Column(accessor="user.email", verbose_name="Email")
    user_type = tables.Column(accessor="user.user_type", verbose_name="User Type")
    faction = tables.Column(accessor="faction.name", verbose_name="Faction")

    class Meta:
        model = LeaderProfile
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "user_type",
            "faction",
        )
        attrs = {"class": "table table-striped table-bordered"}

    url_namespace = None  # handled manually below
    available_actions = ["show", "edit", "delete"]

    def get_url(self, action, record=None, context=None):
        """Route actions based on profile type."""
        if not record:
            return None
        if isinstance(record, LeaderProfile):
            ns = "leaders"
        elif isinstance(record, AttendeeProfile):
            ns = "attendees"
        else:
            return None

        if action == "show":
            return reverse(f"{ns}:show", kwargs={"slug": record.slug})
        if action == "edit":
            return reverse(f"{ns}:edit", kwargs={"slug": record.slug})
        if action == "delete":
            return reverse(f"{ns}:delete", kwargs={"slug": record.slug})
        return None
