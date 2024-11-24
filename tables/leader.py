# faction/tables/leader.py
import django_tables2 as tables
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from user.models import User


class LeaderTable(ActionsColumnMixin, ActionUrlMixin,tables.Table):
    username = tables.Column(accessor="username", verbose_name="Username")
    first_name = tables.Column(accessor="first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="last_name", verbose_name="Last Name")
    email = tables.Column(accessor="email", verbose_name="Email")
    is_admin = tables.Column(accessor="is_admin", verbose_name="Is Faction Admin")
    faction = tables.Column(
        accessor="leaderprofile.faction.name", verbose_name="Faction"
    )
    organization = tables.Column(
        accessor="leaderprofile.organization.name", verbose_name="Organization"
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
            "is_admin",
            "faction",
            "organization",
        )
        attrs = {"class": "table table-striped table-bordered"}
    urls = {
        'add': {
            "url_name": "factions:new_leader",
            "kwargs": {"faction_slug": "faction__slug"},
            "icon": "fa-user-plus",
        },
        'edit': {
            "url_name": "leaders:show",
            "kwargs": {"slug": "slug"},
        },
    }
    url_namespace = "leaders"


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pass the user for permission checks
        super().__init__(*args, **kwargs, user=user)

