# faction/views/attendee.py

from rest_framework import viewsets
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model

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
from enrollment.tables.attendee_class import ClassScheduleTable
from enrollment.tables.attendee import AttendeeEnrollmentTable, AttendeeScheduleTable
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.models.attendee_class import AttendeeClassEnrollment

from ..models.attendee import Attendee, AttendeeProfile
from ..serializers import AttendeeSerializer
from ..forms.attendee import AttendeeForm, PromoteAttendeeForm, RegistrationForm
from ..tables.attendee import AttendeeTable


User = get_user_model()


class IndexView(BaseTableListView):
    model = User
    table_class = AttendeeTable
    template_name = "attendee/list.html"

    context_object_name = "attendee"
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.filter(user_type=User.UserType.ATTENDEE)

        # Check if 'faction_slug' is present in the URL
        faction_slug = self.kwargs.get("faction_slug")
        if faction_slug:
            queryset = queryset.filter(
                attendeeprofile_profile__faction__slug=faction_slug
            )

        return queryset


class CreateView(LoginRequiredMixin, BaseCreateView):
    model = AttendeeProfile
    form_class = AttendeeForm
    template_name = "attendee/form.html"
    # success_url = reverse_lazy("factions:attendees:index")
    action = "Create"
    success_message = "Attendee created successfully!"
    error_message = "Failed to create attendee."

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:attendees:index", kwargs={"faction_slug": faction_slug}
        )


class UpdateView(LoginRequiredMixin, BaseUpdateView):
    model = AttendeeProfile
    form_class = AttendeeForm
    template_name = "attendee/form.html"
    # success_url = reverse_lazy("factions:attendees:index")
    action = "Edit"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:attendees:index", kwargs={"faction_slug": faction_slug}
        )


class PromoteView(LoginRequiredMixin, BaseUpdateView):
    model = AttendeeProfile
    form_class = PromoteAttendeeForm
    template_name = "attendee/promote.html"
    # success_url = reverse_lazy("factions:attendees:index")
    action = "Promote"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:attendees:index", kwargs={"faction_slug": faction_slug}
        )


class DeleteView(LoginRequiredMixin, BaseDeleteView):
    model = AttendeeProfile
    template_name = "attendee/confirm_delete.html"
    # success_url = reverse_lazy("factions:attendees:index")
    action = "Delete"

    def get_success_url(self):
        """
        Dynamically generate the success URL with variables.
        """
        faction_slug = self.object.faction.slug
        return reverse(
            "factions:attendees:index", kwargs={"faction_slug": faction_slug}
        )


class AttendeeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(user_type=User.UserType.ATTENDEE)
    serializer_class = AttendeeSerializer


class ShowView(BaseDetailView):
    model = Attendee
    template_name = "attendee/show.html"
    context_object_name = "attendee"


class ManageView(BaseManageView):
    template_name = "attendee/manage.html"

    def test_func(self):
        return (
            self.request.user.user_type == User.UserType.LEADER
            and self.request.user.is_admin
        )

    def get_tables_config(self):
        attendee_qs = AttendeeEnrollment.objects.select_related(
            "attendee__user"
        ).filter(
            facility_enrollment__facility=self.request.user.attendeeprofile_profile.facility
        )

        return {
            "attendee": {
                "class": AttendeeEnrollmentTable,
                "queryset": attendee_qs,
            }
        }

    def get_forms_config(self):
        return {
            "attendee_form": AttendeeForm,
            "promotion_form": PromoteAttendeeForm,
            "class_form": ClassAssignmentForm,
            "quarters_form": QuartersAssignmentForm,
        }


class DashboardView(BaseDashboardView):
    """
    Dashboard for attendees.
    """

    template_name = "attendee/dashboard.html"
    widgets = ["schedule_widget", "announcements_widget", "resources_widget"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

    def get_widgets_config(self):
        """Define widgets for the attendee dashboard."""
        widgets = {
            "class_schedule": {
                "table_class": AttendeeScheduleTable,
                "queryset": self.get_attendee_schedule_queryset(),
                "priority": 1,
                "title": "Class Schedule",
            },
        }

        return widgets

    def get_attendee_schedule_queryset(self, faction_enrollment=None):
        """Fetch data for class schedule widget."""
        profile = self.request.user.attendeeprofile_profile

        if not faction_enrollment:
            faction_enrollment = self.get_default_faction_enrollment(profile)

        if not faction_enrollment:
            return AttendeeClassEnrollment.objects.none()

        return AttendeeClassEnrollment.objects.filter(
            attendee=profile,
            attendee_enrollment__faction_enrollment=faction_enrollment,
        )

    def get_default_faction_enrollment(self, profile):
        """
        Fetch the default faction enrollment for an attendee profile.
        Returns None if no enrollment is found.
        """
        first_enrollment = profile.enrollments.first()
        return first_enrollment.faction_enrollment if first_enrollment else None


class RegisterAttendeeView(BaseFormView):
    template_name = "attendee/register.html"
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
