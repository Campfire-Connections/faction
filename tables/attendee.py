# faction/tables/attendee.py
import django_tables2 as tables
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.attendee import AttendeeProfile


class AttendeeTable(ActionsColumnMixin, ActionUrlMixin, tables.Table):
    username = tables.Column(accessor="user.username", verbose_name="Username")
    first_name = tables.Column(accessor="user.first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="user.last_name", verbose_name="Last Name")
    email = tables.Column(accessor="user.email", verbose_name="Email")
    faction = tables.Column(accessor="faction.name", verbose_name="Faction")
    organization = tables.Column(
        accessor="organization.name", verbose_name="Organization"
    )

    class Meta:
        model = AttendeeProfile
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
        if not record:
            return super().get_url(action, record=record, context=context)

        if action == "show":
            return reverse("attendees:show", kwargs={"slug": record.slug})
        if action == "edit":
            return reverse("attendees:edit", kwargs={"slug": record.slug})
        if action == "delete":
            return reverse("attendees:delete", kwargs={"slug": record.slug})
        return super().get_url(action, record=record, context=context)
