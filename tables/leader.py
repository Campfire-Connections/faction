# faction/tables/leader.py
import django_tables2 as tables
from django.urls import reverse
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.leader import LeaderProfile


class LeaderTable(ActionsColumnMixin, ActionUrlMixin, tables.Table):
    username = tables.Column(accessor="user.username", verbose_name="Username")
    first_name = tables.Column(accessor="user.first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="user.last_name", verbose_name="Last Name")
    email = tables.Column(accessor="user.email", verbose_name="Email")
    is_admin = tables.Column(accessor="is_admin", verbose_name="Is Faction Admin")
    faction = tables.Column(accessor="faction.name", verbose_name="Faction")
    organization = tables.Column(
        accessor="organization.name", verbose_name="Organization"
    )

    class Meta:
        model = LeaderProfile
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
        "add": {
            "url_name": "factions:new_leader",
            "kwargs": {"faction_slug": "faction__slug"},
            "icon": "fa-user-plus",
        },
        "edit": {
            "url_name": "leaders:show",
            "kwargs": {"slug": "slug"},
        },
    }
    url_namespace = "leaders"

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Pass the user for permission checks
        super().__init__(*args, **kwargs, user=user)

    def get_url(self, action, record=None, context=None):
        """
        Override to ensure show/edit/delete use slug-based leader routes.
        """
        if not record:
            return super().get_url(action, record=record, context=context)

        if action == "show":
            return reverse("leaders:show", kwargs={"slug": record.slug})
        if action == "edit":
            return reverse("leaders:edit", kwargs={"slug": record.slug})
        if action == "delete":
            return reverse("leaders:delete", kwargs={"slug": record.slug})
        return super().get_url(action, record=record, context=context)
