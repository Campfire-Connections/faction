# faction/tables/leader.py
import django_tables2 as tables
from django.urls import reverse
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.leader import LeaderProfile


class LeaderTable(ActionsColumnMixin, ActionUrlMixin, tables.Table):
    username = tables.Column(accessor="user__username", verbose_name="Username")
    first_name = tables.Column(accessor="user__first_name", verbose_name="First Name")
    last_name = tables.Column(accessor="user__last_name", verbose_name="Last Name")
    email = tables.Column(accessor="user__email", verbose_name="Email")
    is_admin = tables.Column(accessor="is_admin", verbose_name="Is Faction Admin")
    faction = tables.Column(accessor="faction__name", verbose_name="Faction")
    organization = tables.Column(
        accessor="organization__name", verbose_name="Organization"
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
            "name": "factions:leaders:new",
            "kwargs": {"faction_slug": "faction_slug"},
            "icon": "fa-user-plus",
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
        faction_slug = (
            (context or {}).get("faction_slug")
            or getattr(record, "faction_slug", None)
            or getattr(getattr(record, "faction", None), "slug", None)
        )
        if action == "add":
            if faction_slug:
                return reverse("factions:leaders:new", kwargs={"faction_slug": faction_slug})
            return None

        if action == "show":
            return reverse(
                "factions:leaders:show",
                kwargs={"faction_slug": faction_slug, "slug": record.slug},
            )
        if action == "edit":
            return reverse(
                "factions:leaders:edit",
                kwargs={"faction_slug": faction_slug, "slug": record.slug},
            )
        if action == "delete":
            return reverse(
                "factions:leaders:delete",
                kwargs={"faction_slug": faction_slug, "slug": record.slug},
            )
        return super().get_url(action, record=record, context=context)
