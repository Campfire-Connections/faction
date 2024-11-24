# faction/tables/faction.py

import django_tables2 as tables
from core.mixins.tables import ActionsColumnMixin, ActionUrlMixin
from ..models.faction import Faction


class FactionTable(ActionsColumnMixin, tables.Table):
    class Meta:
        model = Faction
        template_name = "django_tables2/boostrap4.html"
        fields = ("name", "description", "member_count", "organization", "parent")
        attrs = {"class": "table table-striped table-bordered"}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs, user=user)

    add_url_name = "factions:new"
    edit_url_name = "factions:update"
    delete_url_name = "factions:delete"
    promote_url_name = "factions:promote"


class ChildFactionTable(ActionsColumnMixin, tables.Table):
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
        "add": {"name": "factions:new_child", "kwargs": {"slug": "parent__slug"}},
        "show": {"name": "factions:show", "kwargs": {"slug": "slug"}},
        "edit": {"name": "factions:update", "kwargs": {"slug": "slug"}}
    }
