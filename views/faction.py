# faction/views/faction.py

from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from rest_framework import viewsets
from django.views.generic import TemplateView
from django_tables2 import SingleTableView

from core.views.base import (
    BaseTableListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseManageView,
    BaseChildCreateView,
    BaseSlugOrPkObjectMixin,
    BaseIndexByFilterTableView,
    BaseDetailView,
)
from core.permissions import IsAuthenticatedAndActive
from core.mixins.models import SoftDeleteMixin, SlugMixin, TrackChangesMixin
from core.mixins.views import LoginRequiredMixin, PortalPermissionMixin
from core.utils import get_leader_profile, is_leader_admin

from organization.models.organization import Organization

from ..models.faction import Faction
from ..models.leader import LeaderProfile
from ..forms.faction import FactionForm, ChildFactionForm
from ..tables.faction import FactionTable
from ..tables.roster import RosterTable
from ..serializers import FactionSerializer
from ..selectors import (
    active_factions,
    child_factions_for_faction,
    faction_manage_tables_config,
    get_active_faction_by_id,
    get_active_faction_by_slug,
    roster_for_faction_tree,
)


class RosterView(LoginRequiredMixin, PortalPermissionMixin, SingleTableView):
    model = LeaderProfile
    table_class = RosterTable
    template_name = "faction/roster.html"
    portal_key = "faction"

    def get_faction(self):
        slug = self.kwargs.get("faction_slug") or self.kwargs.get("slug")
        return get_active_faction_by_slug(slug)

    def get_table_data(self):
        return roster_for_faction_tree(self.get_faction())

    def get_queryset(self):
        return self.get_table_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faction"] = self.get_faction()
        return context


class IndexView(BaseTableListView):
    model = Faction
    table_class = FactionTable
    template_name = "faction/index.html"
    context_object_name = "factions"
    page_title = "Factions"

    def get_queryset(self):
        return active_factions().order_by("name")


class CreateView(SlugMixin, BaseCreateView):
    model = Faction
    form_class = FactionForm
    template_name = "faction/form.html"
    success_message = "Faction created successfully!"

    def form_valid(self, form):
        # Ensure slug exists
        if not form.instance.slug:
            form.instance.slug = self.generate_slug("name")

        if not form.instance.organization_id:
            profile = (
                self.request.user.get_profile()
                if hasattr(self.request.user, "get_profile")
                else None
            )
            organization = getattr(profile, "organization", None)
            if organization:
                form.instance.organization = organization
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("factions:show", kwargs={"faction_slug": self.object.slug})


class UpdateView(TrackChangesMixin, BaseUpdateView):
    model = Faction
    form_class = FactionForm
    template_name = "faction/form.html"
    success_message = "Faction updated successfully!"
    success_url = reverse_lazy("factions:index")
    slug_field = "slug"
    slug_url_kwarg = "faction_slug"


class DeleteView(SoftDeleteMixin, BaseDeleteView):
    model = Faction
    template_name = "faction/confirm_delete.html"
    success_message = "Faction deleted successfully!"
    success_url = reverse_lazy("factions:index")
    slug_field = "slug"
    slug_url_kwarg = "faction_slug"


class IndexByOrganizationView(BaseIndexByFilterTableView):
    model = Faction
    table_class = FactionTable
    template_name = "faction/index.html"
    context_object_name = "factions"

    lookup_keys = ["organization_pk", "organization_slug"]
    filter_model = Organization
    filter_field = "organization"
    context_object_name_for_filter = "organization"

    def get_queryset(self):
        # Apply Base logic + filter out soft-deleted
        return super().get_queryset().filter(is_deleted=False)


class ManageView(LoginRequiredMixin, PortalPermissionMixin, BaseManageView):
    template_name = "faction/manage.html"

    def test_func(self):
        return is_leader_admin(self.request.user)

    def get_scope_object(self):
        """Return the faction associated with the leader."""
        slug = self.kwargs.get("faction_slug")
        if slug:
            return get_active_faction_by_slug(slug)
        profile = get_leader_profile(self.request.user)
        faction_id = getattr(profile, "faction_id", None)
        return get_active_faction_by_id(faction_id)

    def get_tables_config(self):
        return faction_manage_tables_config(self.get_scope_object())

    def get_context_data(self, **kwargs):
        # Bypass MultiTableMixin's get_context_data, which expects self.tables, and
        # instead leverage the BaseManageView helpers to build tables from config.
        context = TemplateView.get_context_data(self, **kwargs)

        tables = self.build_tables()
        formatted = []
        for table in tables.values():
            model_meta = getattr(table, "Meta", None)
            model = getattr(model_meta, "model", None) if model_meta else None
            verbose_name = model._meta.verbose_name.title() if model else ""
            verbose_name_plural = model._meta.verbose_name_plural.title() if model else ""
            formatted.append(
                {
                    "table": table,
                    "name": verbose_name or table.__class__.__name__,
                    "name_plural": verbose_name_plural or verbose_name or table.__class__.__name__,
                    "create_url": getattr(table, "add_url", None),
                    "icon": getattr(table, "add_icon", None),
                }
            )

        context.update(
            scope_object=self.get_scope_object(),
            faction=self.get_scope_object(),
            tables_with_names=formatted,
            edit_url=reverse_lazy("factions:update", kwargs={"faction_slug": self.get_scope_object().slug}),
        )
        return context


class ShowView(BaseSlugOrPkObjectMixin, BaseDetailView):
    model = Faction
    template_name = "faction/show.html"
    context_object_name = "faction"
    object_slug_kwarg = "faction_slug"

    def get_object(self, queryset=None):
        slug = (
            self.kwargs.get("child_slug")
            or self.kwargs.get("faction_slug")
            or self.kwargs.get("slug")
        )
        return get_object_or_404(Faction, slug=slug, is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faction = context.get("faction")
        if faction:
            context["child_factions"] = child_factions_for_faction(faction)
            context["parent_faction"] = faction.parent
        return context


class CreateChildView(BaseChildCreateView):
    model = Faction
    form_class = ChildFactionForm
    template_name = "faction/form.html"
    success_message = "Child faction created successfully!"

    parent_model = Faction
    parent_kwarg = "faction_slug"
    parent_field = "parent"

    def form_valid(self, form):
        parent = self.get_parent_object()

        if not parent.organization:
            messages.error(self.request, "Parent faction has no organization.")
            return redirect("factions:manage", faction_slug=parent.slug)

        # Inherit org + parent relationship
        form.instance.organization = parent.organization
        form.instance.parent = parent

        return super().form_valid(form)

    def get_initial(self):
        parent = self.get_parent_object()
        return {"parent": parent, "organization": parent.organization}

    def get_success_url(self):
        parent = self.get_parent_object()
        return reverse(
            "factions:show_child",
            kwargs={"faction_slug": parent.slug, "child_slug": self.object.slug},
        )


class FactionViewSet(viewsets.ModelViewSet):
    queryset = Faction.objects.filter(is_deleted=False)
    serializer_class = FactionSerializer
    permission_classes = [IsAuthenticatedAndActive]
