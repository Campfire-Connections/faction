# faction/tables/attendee.py
import django_tables2 as tables
from pages.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from user.models import User


class AttendeeTable(ActionsColumnMixin, ActionUrlMixin, tables.Table):
    username = tables.Column(accessor="username", verbose_name="Username")
    first_name = tables.Column(accessor="first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="last_name", verbose_name="Last Name")
    email = tables.Column(accessor="email", verbose_name="Email")
    faction = tables.Column(
        accessor="attendeeprofile.faction.name", verbose_name="Faction"
    )
    organization = tables.Column(
        accessor="attendeeprofile.organization.name", verbose_name="Organization"
    )
    # Add more fields as needed

    class Meta:
        model = User
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

