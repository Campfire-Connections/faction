# faction/tables/attendee.py
import django_tables2 as tables
from django.urls import reverse
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.attendee import AttendeeProfile


class AttendeeTable(ActionsColumnMixin, ActionUrlMixin, tables.Table):
    username = tables.Column(accessor="user__username", verbose_name="Username")
    first_name = tables.Column(accessor="user__first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="user__last_name", verbose_name="Last Name")
    email = tables.Column(accessor="user__email", verbose_name="Email")
    faction = tables.Column(accessor="faction__name", verbose_name="Faction")
    organization = tables.Column(
        accessor="organization__name", verbose_name="Organization"
    )

    class Meta:
        model = AttendeeProfile
        verbose_name = "Attendee"
        verbose_name_plural = "Attendees"
        template_name = "django_tables2/bootstrap4.html"
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "faction",
            "organization",
        )
        attrs = {"class": "table table-striped table-bordered"}
    urls = {
        'add': {
            'icon': "fa-user-plus"
        }
    }
    url_namespace = "attendees"
    add_url_name = "attendees:new"
    show_url_name = "attendees:show"
    edit_url_name = "attendees:edit"
    delete_url_name = "attendees:delete"

    def get_url(self, action, record=None, context=None):
        """
        Ensure attendee routes use slug consistently.
        """
        faction_slug = (
            (context or {}).get("faction_slug")
            or getattr(record, "faction_slug", None)
            or getattr(getattr(record, "faction", None), "slug", None)
        )

        if action == "add":
            if faction_slug:
                return reverse("factions:attendees:new", kwargs={"faction_slug": faction_slug})
            return None

        if action == "show":
            return reverse(
                "factions:attendees:show",
                kwargs={"faction_slug": faction_slug, "slug": record.slug},
            )
        if action == "edit":
            return reverse(
                "factions:attendees:edit",
                kwargs={"faction_slug": faction_slug, "slug": record.slug},
            )
        if action == "delete":
            return reverse(
                "factions:attendees:delete",
                kwargs={"faction_slug": faction_slug, "slug": record.slug},
            )
        return super().get_url(action, record=record, context=context)
