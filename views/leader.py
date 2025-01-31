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
from user.models import User
from enrollment.tables.leader import LeaderEnrollmentTable
from enrollment.models.leader import LeaderEnrollment
from enrollment.models.faction import FactionEnrollment

from faction.models.faction import Faction
from faction.models.leader import Leader, LeaderProfile
from faction.serializers import LeaderSerializer
from faction.forms.leader import LeaderForm, PromoteLeaderForm, RegistrationForm
from faction.tables.faction import FactionOverviewTable
from faction.tables.leader import LeaderTable
from faction.charts.faction import FactionReportsChart

User = get_user_model()


class ManageView(BaseManageView):
    template_name = "leader/manage.html"

    def test_func(self):
        return (
            self.request.user.user_type == User.UserType.LEADER
            and self.request.user.is_admin
        )

    def get_tables_config(self):
        leader_qs = LeaderEnrollment.objects.select_related("leader__user").filter(
            facility_enrollment__facility=self.request.user.leaderprofile_profile.faction_enrollment.facility_enrollment.facility
        )

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


class IndexView(BaseTableListView):
    model = User
    table_class = LeaderTable
    template_name = "leader/list.html"

    context_object_name = "leader"
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.filter(user_type=User.UserType.LEADER)

        # Check if 'faction_slug' is present in the URL
        faction_slug = self.kwargs.get("faction_slug")
        if faction_slug:
            queryset = queryset.filter(
                leaderprofile_profile__faction__slug=faction_slug
            )

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
    queryset = User.objects.filter(user_type=User.UserType.LEADER)
    serializer_class = LeaderSerializer


class ShowView(BaseDetailView):
    model = Leader
    template_name = "leader/show.html"
    context_object_name = "leader"


class DashboardView(BaseDashboardView):
    """
    Dashboard for leaders.
    """

    template_name = "leader/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_widgets_config(self):
        """Define widgets for the faction leader or admin dashboard."""
        widgets = {}

        user = self.request.user
        profile = getattr(
            user, "leaderprofile_profile", None
        )  

        if not profile:
            return widgets

        # Shared widgets for both faction leader and admin
        widgets.update(
            {
                "faction_overview": {
                    "table_class": FactionOverviewTable,
                    "queryset": self.get_faction_overview_queryset(),
                    "priority": 1,
                    "title": "Faction Overview",
                },
                # "announcements": {
                #     "table_class": AnnouncementsTable,
                #     "queryset": self.get_announcements_queryset(),
                #     "priority": 4,
                #     "title": "Important Announcements",
                # },
            }
        )

        # Additional widgets for Faction Leader Admins
        if user.is_admin:
            widgets.update(
                {
                    "faction_reports": {
                        "chart_class": FactionReportsChart,
                        "data_source": self.get_faction_reports_data(),
                        "priority": 2,
                        "title": "Faction Enrollment Reports",
                    },
                    # "manage_announcements": {
                    #     "form_class": ManageAnnouncementsForm,
                    #     "priority": 10,
                    #     "title": "Manage Announcements",
                    # },
                }
            )
        else:
            # Widgets specifically for Faction Leaders
            widgets.update(
                {
                    "quick_actions": {
                        "actions": self.get_quick_actions(),
                        "priority": 8,
                        "title": "Quick Actions",
                    },
                }
            )

        return widgets

    def get_faction_overview_queryset(self):
        """Return the queryset for faction overview."""
        user = self.request.user
        profile = getattr(
            user, "leaderprofile_profile", None
        )
        return Faction.objects.filter(pk=profile.faction.pk)

    

    # def get_announcements_queryset(self):
    #     """Return announcements for the faction."""
    #     faction = self.request.user.leaderprofile_profile.faction
    #     return Announcement.objects.filter(faction=faction).order_by("-created_at")

    
    def get_faction_reports_data(self):
        """Return data for faction reports."""
        faction = self.request.user.leaderprofile_profile.faction
        # Prepare enrollment data
        enrollments_by_faction = (
            FactionEnrollment.objects.filter(faction=faction)
            .values("faction__name")
            .annotate(count=Count("id"))
        )

        # Convert queryset to a list of dictionaries for the chart
        return [
            {"label": item["faction__name"], "count": item["count"]}
            for item in enrollments_by_faction
        ]


    def get_quick_actions(self):
        """Return quick actions for the leader."""
        return [
            #{"label": "Create Announcement", "url": reverse("announcements:create")},
            {"label": "Add Attendee", "url": reverse("factions:attendees:new")},
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
