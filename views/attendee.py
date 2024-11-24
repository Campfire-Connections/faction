# faction/views/attendee.py

from rest_framework import viewsets
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView as _CreateView,
    UpdateView as _UpdateView,
    DeleteView as _DeleteView,
    DetailView as _DetailView,
)
from django.urls import reverse_lazy
from django_tables2 import SingleTableView, SingleTableMixin
from django.contrib.auth import get_user_model

from core.mixins.forms import SuccessMessageMixin, FormValidMixin
from user.models import User
from user.mixins import AdminRequiredMixin
from organization.models.organization import (
    Organization,
    OrganizationLabels,
)

from ..models.faction import Faction
from ..models.attendee import AttendeeProfile
from ..serializers import AttendeeSerializer
from ..forms.attendee import AttendeeForm
from ..tables.attendee import AttendeeTable


User = get_user_model()


class IndexByFactionView(SingleTableView):
    model = User
    table_class = AttendeeTable
    template_name = "attendee/index.html"

    def get_queryset(self):
        faction_slug = self.kwargs.get("slug")
        return User.objects.filter(
            user_type="ATTENDEE", attendeeprofile__faction__slug=faction_slug
        ).select_related("attendeeprofile")


class IndexByOrganizationView(SingleTableView):
    model = User
    table_class = AttendeeTable
    template_name = "attendee/index.html"

    def get_queryset(self):
        org_slug = self.kwargs.get("slug")
        return User.objects.filter(
            user_type="ATTENDEE", attendeeprofile__faction__organization__slug=org_slug
        ).select_related("attendeeprofile")


class IndexView(SingleTableView):
    model = User
    table_class = AttendeeTable
    template_name = "attendee/index.html"

    def get_queryset(self):
        return User.objects.filter(user_type="ATTENDEE").select_related(
            "attendeeprofile"
        )


class CreateView(AdminRequiredMixin, SuccessMessageMixin, FormValidMixin, _CreateView):
    model = AttendeeProfile
    form_class = AttendeeForm
    template_name = "attendee/form.html"
    success_message = "Attendee created successfully!"
    success_url = reverse_lazy("attendee_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Create"
        return context


class UpdateView(AdminRequiredMixin, SuccessMessageMixin, FormValidMixin, _UpdateView):
    model = AttendeeProfile
    form_class = AttendeeForm
    template_name = "attendee/form.html"
    success_message = "Attendee updated successfully!"
    success_url = reverse_lazy("attendee_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Edit"
        return context

class PromoteView(_UpdateView):
    pass

class DeleteView(AdminRequiredMixin, SuccessMessageMixin, _DeleteView):
    model = AttendeeProfile
    template_name = "attendee/confirm_delete.html"
    success_message = "Attendee deleted successfully!"
    success_url = reverse_lazy("attendee_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Delete"
        return context


class AttendeeViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(user_type=User.UserType.ATTENDEE)
    serializer_class = AttendeeSerializer


class ShowView(_DetailView):
    model = AttendeeProfile
    template_name = "attendee/show.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Details"
        return context


class ManageView(
    LoginRequiredMixin, UserPassesTestMixin, SingleTableMixin, TemplateView
):
    template_name = "attendee/manage.html"
    table_class = AttendeeTable

    def test_func(self):
        user = self.request.user
        return user.is_admin and user.user_type == "LEADER"

    def get_table_data(self):
        faction = self.request.user.leaderprofile.faction
        return User.objects.filter(
            user_type="ATTENDEE", attendeeprofile__faction=faction
        )

    def post(self, request, *args, **kwargs):
        if "edit" in request.POST:
            attendee_id = request.POST.get("attendee_id")
            return redirect("attendee:edit", pk=attendee_id)
        elif "delete" in request.POST:
            attendee_id = request.POST.get("attendee_id")
            return redirect("attendee:delete", pk=attendee_id)
        elif "enroll" in request.POST:
            attendee_id = request.POST.get("attendee_id")
            return redirect("attendee:enroll", pk=attendee_id)
        return super().post(request, *args, **kwargs)
