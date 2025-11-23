# faction/views/attendee.py

from rest_framework import viewsets
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login

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
    get_attendee_resources,
    get_attendee_announcements,
    get_attendee_schedule,
)

from enrollment.tables.attendee_class import ClassScheduleTable
from enrollment.tables.attendee import AttendeeEnrollmentTable, AttendeeScheduleTable
from enrollment.models.attendee import AttendeeEnrollment
from enrollment.forms.attendee import AttendeeClassAssignmentForm, AttendeeQuartersAssignmentForm

from ..models.attendee import AttendeeProfile
from faction.models.faction import Faction
from ..serializers import AttendeeSerializer
from ..forms.attendee import AttendeeForm, PromoteAttendeeForm, RegistrationForm
from ..tables.attendee import AttendeeTable


class IndexView(FactionScopedMixin, BaseTableListView):
    model = AttendeeProfile
    table_class = AttendeeTable
    template_name = "attendee/list.html"
    context_object_name = "attendee"
    paginate_by = 10
    faction_kwarg = "slug"

    def get_scope_faction(self):
        slug = self.kwargs.get("slug")
        if slug:
            return get_object_or_404(Faction, slug=slug)
        return super().get_scope_faction()

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related("user", "faction", "organization")
        faction = self.get_scope_faction()
        if faction:
            faction_ids = []
            stack = [faction]
            while stack:
                current = stack.pop()
                faction_ids.append(current.id)
                stack.extend(list(current.children.all()))
            queryset = queryset.filter(faction_id__in=faction_ids)
        return queryset.order_by("user__username")

    def get_table_data(self):
        return list(self.get_queryset())


class CreateView(LoginRequiredMixin, BaseCreateView):
    model = AttendeeProfile
    form_class = AttendeeForm
    template_name = "attendee/form.html"
    action = "Create"
    success_message = "Attendee created successfully!"
    error_message = "Failed to create attendee."

    def get_success_url(self):
        return reverse(
            "factions:attendees:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class UpdateView(LoginRequiredMixin, BaseUpdateView):
    model = AttendeeProfile
    form_class = AttendeeForm
    template_name = "attendee/form.html"
    action = "Edit"

    def get_success_url(self):
        return reverse(
            "factions:attendees:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class PromoteView(LoginRequiredMixin, BaseUpdateView):
    model = AttendeeProfile
    form_class = PromoteAttendeeForm
    template_name = "attendee/promote.html"
    action = "Promote"

    def get_success_url(self):
        return reverse(
            "factions:attendees:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class DeleteView(LoginRequiredMixin, BaseDeleteView):
    model = AttendeeProfile
    template_name = "attendee/confirm_delete.html"
    action = "Delete"

    def get_success_url(self):
        return reverse(
            "factions:attendees:index",
            kwargs={"faction_slug": self.object.faction.slug},
        )


class AttendeeViewSet(viewsets.ModelViewSet):
    queryset = AttendeeProfile.objects.select_related("user", "faction")
    serializer_class = AttendeeSerializer


class ShowView(BaseDetailView):
    model = AttendeeProfile
    template_name = "attendee/show.html"
    context_object_name = "attendee"


class ManageView(PortalPermissionMixin, FactionScopedMixin, BaseManageView):
    template_name = "attendee/manage.html"
    portal_key = "faction"

    def get_tables_config(self):
        faction = self.get_scope_faction()
        attendee_qs = AttendeeEnrollment.objects.select_related("attendee__user")
        if faction:
            attendee_qs = attendee_qs.filter(faction_enrollment__faction=faction)
        else:
            attendee_qs = attendee_qs.none()

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
            "class_form": AttendeeClassAssignmentForm,
            "quarters_form": AttendeeQuartersAssignmentForm,
        }


class DashboardView(PortalPermissionMixin, FactionScopedMixin, BaseDashboardView):
    """
    Dashboard for attendees.
    """

    template_name = "attendee/dashboard.html"
    portal_key = "attendee"

    def get_attendee_schedule_widget(self, _definition):
        profile = getattr(self.request.user, "attendeeprofile_profile", None)
        queryset = get_attendee_schedule(profile)
        return {"table_class": AttendeeScheduleTable, "queryset": queryset}

    def get_attendee_announcements_widget(self, _definition):
        faction = self.get_scope_faction()
        items = get_attendee_announcements(faction)
        return {"items": items}

    def get_attendee_resources_widget(self, _definition):
        faction = self.get_scope_faction()
        return {"items": get_attendee_resources(faction)}


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
