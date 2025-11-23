# faction/views/leader.py

from rest_framework import viewsets
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model, authenticate, login

from core.views.base import (
    BaseManageView,
    BaseTableListView,
    BaseCreateView,
    BaseDeleteView,
    BaseDetailView,
    BaseUpdateView,
    BaseFormView,
    BaseDashboardView,
)
from core.mixins.views import FactionScopedMixin, PortalPermissionMixin, LoginRequiredMixin
from core.dashboard_data import (
    get_faction_enrollment_counts,
    get_leader_metrics,
    get_leader_resource_links,
)
from core.utils import is_leader_admin

from enrollment.tables.leader import LeaderEnrollmentTable
from enrollment.models.leader import LeaderEnrollment

from faction.models.faction import Faction
from faction.models.leader import LeaderProfile
from faction.serializers import LeaderSerializer
from faction.forms.leader import LeaderForm, PromoteLeaderForm, RegistrationForm, QuartersAssignmentForm
from faction.tables.faction import FactionOverviewTable
from faction.tables.leader import LeaderTable

User = get_user_model()


class ManageView(PortalPermissionMixin, FactionScopedMixin, BaseManageView):
    template_name = "leader/manage.html"
    portal_key = "faction"

    def get_tables_config(self):
        faction = self.get_scope_faction()
        leader_qs = LeaderEnrollment.objects.select_related("leader__user")
        if faction:
            leader_qs = leader_qs.filter(faction_enrollment__faction=faction)
        else:
            leader_qs = leader_qs.none()

        return {
            "leader": {
                "class": LeaderEnrollmentTable,
                "queryset": leader_qs,
            }
        }

    def get_forms_config(self):
        return {
            "leader_form": LeaderForm,
            "promotion_form": PromoteLeaderForm,
            "quarters_form": QuartersAssignmentForm,
        }


class IndexView(FactionScopedMixin, BaseTableListView):
    model = LeaderProfile
    table_class = LeaderTable
    template_name = "leader/list.html"
    context_object_name = "leader"
    paginate_by = 10
    faction_kwarg = "slug"

    def get_queryset(self):
        queryset = LeaderProfile.objects.select_related("user", "faction", "organization")
        faction = self.get_scope_faction()
        if faction:
            queryset = queryset.filter(faction=faction)
        return queryset


class CreateView(LoginRequiredMixin, BaseCreateView):
    model = LeaderProfile
    form_class = LeaderForm
    template_name = "leader/form.html"

    def get_success_url(self):
        return reverse(
            "factions:leaders:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class UpdateView(LoginRequiredMixin, BaseUpdateView):
    model = LeaderProfile
    form_class = LeaderForm
    template_name = "leader/form.html"
    action = "Edit"

    def get_success_url(self):
        return reverse(
            "factions:leaders:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class PromoteView(LoginRequiredMixin, BaseUpdateView):
    model = LeaderProfile
    form_class = PromoteLeaderForm
    template_name = "leader/promote.html"
    action = "Promote"

    def get_success_url(self):
        return reverse(
            "factions:leaders:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class DeleteView(LoginRequiredMixin, BaseDeleteView):
    model = LeaderProfile
    template_name = "leader/confirm_delete.html"
    action = "Delete"

    def get_success_url(self):
        return reverse(
            "factions:leaders:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class LeaderViewSet(viewsets.ModelViewSet):
    queryset = LeaderProfile.objects.select_related("user", "faction")
    serializer_class = LeaderSerializer


class ShowView(BaseDetailView):
    model = LeaderProfile
    template_name = "leader/show.html"
    context_object_name = "leader"


class DashboardView(PortalPermissionMixin, FactionScopedMixin, BaseDashboardView):
    """
    Dashboard for leaders.
    """

    template_name = "leader/dashboard.html"
    portal_key = "faction"

    def get_faction_overview_queryset(self):
        """Return the queryset for faction overview."""
        faction = self.get_scope_faction()
        if not faction:
            return Faction.objects.none()
        return Faction.objects.filter(pk=faction.pk)

    def get_quick_actions(self):
        """Return quick actions for the leader."""
        return [
            {"label": "Add Attendee", "url": reverse("attendees:new")},
        ]

    def is_leader_admin(self):
        return is_leader_admin(self.request.user)

    def is_leader_standard(self):
        return not is_leader_admin(self.request.user)

    def get_leader_metrics_widget(self, _definition):
        faction = self.get_scope_faction()
        metrics = get_leader_metrics(faction)
        if not metrics:
            return None
        return {"metrics": metrics}

    def get_faction_overview_widget(self, _definition):
        queryset = self.get_faction_overview_queryset()
        return {"table_class": FactionOverviewTable, "queryset": queryset}

    def get_leader_chart_widget(self, _definition):
        faction = self.get_scope_faction()
        data = get_faction_enrollment_counts(faction)
        if not data:
            return None
        labels = [item["label"] for item in data]
        values = [item["count"] for item in data]
        config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [
                    {
                        "label": "Enrollments",
                        "backgroundColor": "#0077cc",
                        "borderColor": "#005999",
                        "data": values,
                    }
                ],
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "scales": {"y": {"beginAtZero": True}},
            },
        }
        return {"chart_config": config}

    def get_leader_actions_widget(self, _definition):
        return {"actions": self.get_quick_actions()}

    def get_leader_resources_widget(self, _definition):
        faction = self.get_scope_faction()
        resources = get_leader_resource_links(faction)
        return {"items": resources}


class RegisterLeaderView(BaseFormView):
    template_name = "leader/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get("username")
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=raw_password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)
