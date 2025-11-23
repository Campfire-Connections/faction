# faction/tables/faction.py

import django_tables2 as tables
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.faction import Faction


class FactionTable(ActionsColumnMixin, tables.Table):
    class Meta:
        model = Faction
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name", "description", "member_count", "organization", "parent")
        attrs = {"class": "table table-striped table-bordered"}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs, user=user)

    url_namespace = "factions"
    urls = {
        "add": {"name": "factions:new"},
        "show": {"name": "factions:show", "kwargs": {"slug": "slug"}},
        "edit": {"name": "factions:update", "kwargs": {"slug": "slug"}},
        "delete": {"name": "factions:delete", "kwargs": {"slug": "slug"}},
    }


class ChildFactionTable(ActionsColumnMixin, tables.Table):
    debug_mode = False

    class Meta:
        model = Faction
        fields = ("name", "description", "member_count")
        template_name = "django_tables2/bootstrap4.html"
        attrs = {"class": "table table-striped table-bordered"}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs, user=user)

    url_namespace = "factions"
    urls = {
        "add": {"name": "factions:new_child", "kwargs": {"faction_slug": "parent__slug"}},
        "show": {
            "name": "factions:show_child",
            "kwargs": {"faction_slug": "parent__slug", "child_slug": "slug"},
        },
        "edit": {"name": "factions:update", "kwargs": {"faction_slug": "slug"}},
    }


class FactionOverviewTable(tables.Table):
    name = tables.Column(verbose_name="Faction Name")
    #leaders_count = tables.Column(verbose_name="Number of Leaders", accessor="leaders.count")
    #members_count = tables.Column(verbose_name="Number of Attendees", accessor="attendees.count")

    class Meta:
        model = Faction
        fields = ["name"]#, "leaders_count", "members_count"]
