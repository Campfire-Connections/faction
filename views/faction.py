# faction/views/faction.py

from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import (
    ListView as _ListView,
    CreateView as _CreateView,
    UpdateView as _UpdateView,
    DeleteView as _DeleteView,
    DetailView as _DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django_tables2 import MultiTableMixin, SingleTableView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import ValidationError

from organization.models.organization import Organization
from enrollment.models.faction import FactionEnrollment
from enrollment.tables.faction import FactionEnrollmentTable
from user.models import User
from core.mixins.forms import FormValidationMixin, SuccessMessageMixin
from core.mixins.models import SlugMixin, TrackChangesMixin, SoftDeleteMixin

from ..models.faction import Faction
from ..forms.faction import FactionForm, ChildFactionForm
from ..serializers import FactionSerializer
from ..tables.faction import FactionTable, ChildFactionTable
from ..tables.leader import LeaderTable
from ..tables.attendee import AttendeeTable


class IndexView(_ListView):
    model = Faction
    template_name = "faction/index.html"
    context_object_name = "factions"


class CreateView(SlugMixin, SuccessMessageMixin, FormValidationMixin, _CreateView):
    model = Faction
    form_class = FactionForm
    template_name = "faction/form.html"
    success_message = "Faction created successfully!"
    success_url = reverse_lazy("factions:manage")

    def form_valid(self, form):
        if not form.instance.slug:
            form.instance.slug = self.generate_slug(field="name")
        form.instance.organization = get_object_or_404(
            Organization, pk=self.request.user.organization_id
        )
        return super().form_valid(form)


class UpdateView(
    TrackChangesMixin, SuccessMessageMixin, FormValidationMixin, _UpdateView
):
    model = Faction
    form_class = FactionForm
    template_name = "faction/form.html"
    success_message = "Faction updated successfully!"
    success_url = reverse_lazy("factions:index")

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)


class DeleteView(SoftDeleteMixin, SuccessMessageMixin, _DeleteView):
    model = Faction
    template_name = "faction/confirm_delete.html"
    success_message = "Faction deleted successfully!"
    success_url = reverse_lazy("factions:index")


class IndexByOrganizationView(_ListView):
    model = Faction
    template_name = "faction/index.html"
    context_object_name = "factions"

    def get_queryset(self):
        organization_lookup = self.kwargs.get("organization_pk") or self.kwargs.get(
            "organization_slug"
        )
        organization = get_object_or_404(
            Organization,
            pk=(
                organization_lookup
                if organization_lookup.isdigit()
                else organization_lookup
            ),
        )
        return Faction.objects.filter(
            organization=organization, is_deleted=False
        )  # Filter out deleted

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organization_lookup = self.kwargs.get("organization_pk") or self.kwargs.get(
            "organization_slug"
        )
        organization = get_object_or_404(
            Organization,
            pk=(
                organization_lookup
                if organization_lookup.isdigit()
                else organization_lookup
            ),
        )
        context["organization"] = organization
        return context


class ManageView(
    LoginRequiredMixin, UserPassesTestMixin, MultiTableMixin, TemplateView
):
    template_name = "faction/manage.html"

    def get_tables(self):
        faction = self.get_faction()
        child_factions = Faction.objects.filter(
            parent=faction, is_deleted=False
        )  # Avoid showing deleted factions

        leaders_qs = User.objects.filter(
            user_type="LEADER", leaderprofile__faction=faction
        ).select_related("leaderprofile")
        attendees_qs = User.objects.filter(
            user_type="ATTENDEE", attendeeprofile__faction__parent=faction
        ).select_related("attendeeprofile")

        return [
            LeaderTable(leaders_qs),
            AttendeeTable(attendees_qs),
            FactionEnrollmentTable(FactionEnrollment.objects.filter(faction=faction)),
            ChildFactionTable(child_factions),
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        faction = self.get_faction()

        tables_with_names = [
            {
                "table": table,
                "name": self.get_table_name(table),
                "create_url": table.get_url("add", context={"slug": faction.slug}),
                "icon": getattr(table, "add_icon", None),
            }
            for table in self.get_tables()
        ]

        context.update(
            {
                "tables_with_names": tables_with_names,
                "faction": faction,
            }
        )
        return context

    def get_faction(self):
        user = self.request.user
        profile = user.leaderprofile
        return get_object_or_404(Faction, id=profile.faction_id, is_deleted=False)

    def test_func(self):
        return self.request.user.user_type == "LEADER" and self.request.user.is_admin

    def get_table_name(self, table):
        if table.Meta.model == User:
            first_user = table.data.data.first()
            if first_user and hasattr(first_user, "user_type"):
                if first_user.user_type == "LEADER":
                    return "Leader"
                if first_user.user_type == "ATTENDEE":
                    return "Attendee"
            return "Users"
        return table.Meta.model._meta.verbose_name.title()


class ShowView(_DetailView):
    model = Faction
    template_name = "faction/show.html"
    context_object_name = "faction"


class CreateChildView(SuccessMessageMixin, FormValidationMixin, _CreateView):
    model = Faction
    template_name = "faction/form.html"
    form_class = ChildFactionForm
    success_message = "Child faction created successfully!"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Fetch the parent faction based on the URL slug and pass it to the form
        parent_faction = get_object_or_404(
            Faction.objects.filter(slug=self.kwargs["slug"])
        )
        kwargs["initial"] = {
            "parent": parent_faction,
            "organization": parent_faction.organization,
        }
        return kwargs

    def form_valid(self, form):
        """Set parent faction and organization from the parent."""
        parent_faction = get_object_or_404(
            Faction.objects.filter(slug=self.kwargs["slug"])
        )
        # Check if the parent faction has an associated organization
        if not parent_faction.organization:
            messages.error(
                self.request,
                "The parent faction does not have an associated organization.",
            )
            return redirect(
                reverse_lazy("factions:manage")
            )  # Redirect to manage or some appropriate page

        # Set the parent and organization fields
        form.instance.parent = parent_faction
        form.instance.organization = parent_faction.organization

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("factions:show", kwargs={"slug": self.object.slug})


class FactionViewSet(viewsets.ModelViewSet):
    queryset = Faction.objects.filter(
        is_deleted=False
    )  # Filter out soft-deleted factions
    serializer_class = FactionSerializer
