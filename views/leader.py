# faction/views/leader.py

from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.db.models import Count

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
from core.mixins.views import (
    FactionScopedMixin,
    PortalPermissionMixin,
)
from core.widgets import ActionsWidget, ChartWidget, TableWidget, MetricsWidget, ListWidget
from user.models import User
from enrollment.tables.leader import LeaderEnrollmentTable
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.faction import FactionEnrollment

from faction.models.faction import Faction
from faction.models.leader import LeaderProfile
from faction.serializers import LeaderSerializer
from faction.forms.leader import LeaderForm, PromoteLeaderForm, RegistrationForm
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

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user", "faction", "organization")
        faction = self.get_scope_faction()
        if faction:
            queryset = queryset.filter(faction=faction)
        return queryset


class CreateView(LoginRequiredMixin, BaseCreateView):
    model = LeaderProfile
    form_class = LeaderForm
    template_name = "leader/form.html"

    def get_success_url(self):
        faction_slug = self.object.faction.slug
        return reverse("factions:leaders:index", kwargs={"faction_slug": faction_slug})


class UpdateView(LoginRequiredMixin, BaseUpdateView):
    model = LeaderProfile
    form_class = LeaderForm
    template_name = "leader/form.html"
    action = "Edit"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse("factions:leaders:index", kwargs={"faction_slug": faction_slug})


class PromoteView(LoginRequiredMixin, BaseUpdateView):
    model = LeaderProfile
    form_class = PromoteLeaderForm
    template_name = "leader/promote.html"
    # success_url = reverse_lazy("factions:leaders:index")
    action = "Promote"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse("factions:leaders:index", kwargs={"faction_slug": faction_slug})


class DeleteView(LoginRequiredMixin, BaseDeleteView):
    model = LeaderProfile
    template_name = "leader/confirm_delete.html"
    action = "Delete"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse("factions:leaders:index", kwargs={"faction_slug": faction_slug})


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
    
    def get_dashboard_widgets(self):
        faction = self.get_scope_faction()
        if not faction:
            return []

        widgets = [
            MetricsWidget(
                self.request,
                title="Snapshot",
                metrics=self.get_leader_metrics(),
                priority=0,
                width=12,
            ),
            TableWidget(
                self.request,
                title="Faction Overview",
                table_class=FactionOverviewTable,
                queryset=self.get_faction_overview_queryset(),
                priority=1,
                width=6,
            )
        ]

        if self.request.user.is_admin:
            widgets.append(
                ChartWidget(
                    self.request,
                    title="Faction Enrollment Reports",
                    chart_config=self.get_faction_reports_chart_config(),
                    priority=2,
                    width=6,
                )
            )
            widgets.append(
                ListWidget(
                    self.request,
                    title="Leadership Resources",
                    items=self.get_leader_resources(),
                    priority=6,
                    width=6,
                )
            )
        else:
            widgets.append(
                ActionsWidget(
                    self.request,
                    title="Quick Actions",
                    actions=self.get_quick_actions(),
                    priority=8,
                    width=4,
                )
            )
            widgets.append(
                ListWidget(
                    self.request,
                    title="Next Steps",
                    items=self.get_leader_resources(),
                    priority=9,
                    width=8,
                )
            )
        return widgets

    def get_faction_overview_queryset(self):
        """Return the queryset for faction overview."""
        faction = self.get_scope_faction()
        if not faction:
            return Faction.objects.none()
        return Faction.objects.filter(pk=faction.pk)

    

    # def get_announcements_queryset(self):
    #     """Return announcements for the faction."""
    #     faction = self.request.user.leaderprofile_profile.faction
    #     return Announcement.objects.filter(faction=faction).order_by("-created_at")

    
    def get_faction_reports_data(self):
        """Return aggregated enrollment data for the chart widget."""
        faction = self.request.user.leaderprofile_profile.faction
        enrollments_by_faction = (
            FactionEnrollment.objects.filter(faction=faction)
            .values("faction__name")
            .annotate(count=Count("id"))
        )

        return [
            {"label": item["faction__name"], "count": item["count"]}
            for item in enrollments_by_faction
        ]

    def get_faction_reports_chart_config(self):
        data = self.get_faction_reports_data()
        labels = [item["label"] for item in data]
        values = [item["count"] for item in data]
        return {
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


    def get_quick_actions(self):
        """Return quick actions for the leader."""
        return [
            #{"label": "Create Announcement", "url": reverse("announcements:create")},
            {"label": "Add Attendee", "url": reverse("attendees:new")},
        ]

    def get_leader_metrics(self):
        faction = self.get_scope_faction()
        attendee_count = faction.member_count(user_type="attendee") if faction else 0
        leader_count = faction.member_count(user_type="leader") if faction else 0
        return [
            {"label": "Leaders", "value": leader_count},
            {"label": "Attendees", "value": attendee_count},
        ]

    def get_leader_resources(self):
        return [
            {
                "title": "Faction Roster",
                "subtitle": "Review attendee contact info.",
                "url": reverse("attendees:index"),
            },
            {
                "title": "Weekly Schedule",
                "subtitle": "Confirm your next session assignments.",
                "url": reverse("leaders:manage"),
            },
        ]



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
