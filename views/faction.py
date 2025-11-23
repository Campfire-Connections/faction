# faction/views/faction.py

from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from rest_framework import viewsets
from django.views.generic import TemplateView
from django_tables2 import MultiTableMixin, SingleTableView

from core.views.base import (
    BaseListView,
    BaseCreateView,
    BaseUpdateView,
    BaseDeleteView,
    BaseManageView,
    BaseChildCreateView,
    BaseSlugOrPkObjectMixin,
    BaseIndexByFilterTableView,
    BaseDetailView,
)
from core.mixins.models import SoftDeleteMixin, SlugMixin, TrackChangesMixin
from core.mixins.views import LoginRequiredMixin, PortalPermissionMixin
from core.views.base_helpers import build_tables_from_config
from core.utils import get_leader_profile, is_leader_admin

from organization.models.organization import Organization
from enrollment.models.faction import FactionEnrollment
from user.models import User

from ..models.faction import Faction
from ..models.leader import LeaderProfile
from ..models.attendee import AttendeeProfile
from ..forms.faction import FactionForm, ChildFactionForm
from ..tables.faction import FactionTable, ChildFactionTable
from ..tables.attendee import AttendeeTable
from ..tables.leader import LeaderTable
from ..tables.roster import RosterTable
from ..serializers import FactionSerializer


class RosterView(LoginRequiredMixin, PortalPermissionMixin, SingleTableView):
    model = LeaderProfile
    table_class = RosterTable
    template_name = "faction/roster.html"
    portal_key = "faction"

    def get_faction(self):
        slug = self.kwargs.get("faction_slug") or self.kwargs.get("slug")
        return get_object_or_404(Faction, slug=slug, is_deleted=False)

    def _faction_and_descendants(self, faction):
        ids = []
        stack = [faction]
        while stack:
            current = stack.pop()
            ids.append(current.id)
            stack.extend(list(current.children.all()))
        return ids

    def get_table_data(self):
        faction = self.get_faction()
        faction_ids = self._faction_and_descendants(faction)
        leaders_qs = LeaderProfile.objects.filter(
            faction_id__in=faction_ids
        ).select_related("user", "organization", "faction")
        attendees_qs = AttendeeProfile.objects.filter(
            faction_id__in=faction_ids
        ).select_related("user", "organization", "faction")
        return list(leaders_qs) + list(attendees_qs)

    def get_queryset(self):
        return self.get_table_data()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faction"] = self.get_faction()
        return context


class IndexView(BaseListView):
    model = Faction
    template_name = "faction/index.html"
    context_object_name = "factions"


class CreateView(SlugMixin, BaseCreateView):
    model = Faction
    form_class = FactionForm
    template_name = "faction/form.html"
    success_message = "Faction created successfully!"
    success_url = reverse_lazy("factions:manage")

    def form_valid(self, form):
        # Ensure slug exists
        if not form.instance.slug:
            form.instance.slug = self.generate_slug("name")

        # Attach to the user's organization
        form.instance.organization = get_object_or_404(
            Organization, pk=self.request.user.organization_id
        )
        return super().form_valid(form)


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
        profile = get_leader_profile(self.request.user)
        faction_id = getattr(profile, "faction_id", None)
        return get_object_or_404(Faction, id=faction_id, is_deleted=False)

    def get_tables(self):
        tables_config = self.get_tables_config()
        tables = {}
        for name, cfg in tables_config.items():
            table_class = cfg["class"]
            qs = cfg["queryset"]
            tables[name] = table_class(qs, request=self.request, user=self.request.user)
        return tables

    def get_tables_config(self):
        faction = self.get_scope_object()

        leaders_qs = User.objects.filter(
            user_type="LEADER", leaderprofile__faction=faction
        ).select_related("leaderprofile")

        attendees_qs = User.objects.filter(
            user_type="ATTENDEE", attendeeprofile__faction__parent=faction
        ).select_related("attendeeprofile")

        child_factions_qs = Faction.objects.filter(
            parent=faction, is_deleted=False
        )

        return {
            "leaders": {
                "class": LeaderTable,
                "queryset": leaders_qs,
            },
            "attendees": {
                "class": AttendeeTable,
                "queryset": attendees_qs,
            },
            "enrollments": {
                "class": FactionEnrollmentTable,
                "queryset": FactionEnrollment.objects.filter(faction=faction),
            },
            "child_factions": {
                "class": ChildFactionTable,
                "queryset": child_factions_qs,
            },
        }


class ShowView(BaseSlugOrPkObjectMixin, BaseDetailView):
    model = Faction
    template_name = "faction/show.html"
    context_object_name = "faction"
    object_slug_kwarg = "faction_slug"


class CreateChildView(BaseChildCreateView):
    model = Faction
    form_class = ChildFactionForm
    template_name = "faction/form.html"
    success_message = "Child faction created successfully!"

    parent_model = Faction
    parent_kwarg = "slug"
    parent_field = "parent"

    def form_valid(self, form):
        parent = self.get_parent_object()

        if not parent.organization:
            messages.error(self.request, "Parent faction has no organization.")
            return redirect("factions:manage")

        # Inherit org + parent relationship
        form.instance.organization = parent.organization
        form.instance.parent = parent

        return super().form_valid(form)

    def get_initial(self):
        parent = self.get_parent_object()
        return {"parent": parent, "organization": parent.organization}

    def get_success_url(self):
        return reverse("factions:show", kwargs={"slug": self.object.slug})


class FactionViewSet(viewsets.ModelViewSet):
    queryset = Faction.objects.filter(is_deleted=False)
    serializer_class = FactionSerializer
