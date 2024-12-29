# faction/views/leader.py

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

from core.views.base import BaseDashboardView
from user.models import User
from user.mixins import AdminRequiredMixin
from organization.models.organization import (
    Organization,
    OrganizationLabels,
)

from ..models.faction import Faction
from ..models.leader import LeaderProfile
from ..serializers import LeaderSerializer
from ..forms.leader import LeaderForm, LeaderProfileForm
from ..tables.leader import LeaderTable


class ManageView(
    LoginRequiredMixin, UserPassesTestMixin, SingleTableView, TemplateView
):
    template_name = "leader/manage.html"
    table_class = LeaderTable

    def test_func(self):
        user = self.request.user
        return user.is_admin and user.user_type == "LEADER"

    def get_table_data(self):
        faction = self.request.user.leaderprofile.faction
        return User.objects.filter(user_type="LEADER", leaderprofile__faction=faction)

    def post(self, request, *args, **kwargs):
        leader_id = request.POST.get("leader_id")
        if "edit" in request.POST:
            return redirect("leader:edit", pk=leader_id)
        elif "delete" in request.POST:
            return redirect("leader:delete", pk=leader_id)
        elif "enroll" in request.POST:
            return redirect("leader:enroll", pk=leader_id)
        elif "promote" in request.POST:
            leader = get_object_or_404(User, pk=leader_id)
            leader.is_admin = True
            leader.save()
            return redirect("leader:manage")
        return super().post(request, *args, **kwargs)


class IndexView(SingleTableView):
    model = User
    table_class = LeaderTable
    template_name = "leader/index.html"

    def get_queryset(self):
        results = User.objects.filter(user_type="LEADER").select_related(
            "leaderprofile", "leaderprofile__faction"
        )
        return results

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_header_text"] = "Leaders"
        return context


class CreateView(AdminRequiredMixin, _CreateView):
    model = LeaderProfile
    form_class = LeaderForm
    template_name = "leader/form.html"
    success_url = reverse_lazy("leader_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "slug" in self.kwargs:
            # If a faction slug is provided, pass the faction to the context
            context["faction"] = get_object_or_404(Faction, slug=self.kwargs["slug"])
        return context

    def form_valid(self, form):
        if "slug" in self.kwargs:
            # If creating a leader for a specific faction
            faction = get_object_or_404(Faction, slug=self.kwargs["slug"])
            form.instance.faction = faction
        return super().form_valid(form)

    def get_success_url(self):
        if "slug" in self.kwargs:
            # Redirect to the faction leader list after creation
            return reverse_lazy("factions:show", kwargs={"slug": self.kwargs["slug"]})
        return reverse_lazy("leaders:index")  # Redirect to global leader list


class UpdateView(AdminRequiredMixin, _UpdateView):
    model = User
    template_name = "leader/form.html"
    form_class = LeaderForm
    success_url = reverse_lazy(
        "leaders:index"
    )  # Update this to the appropriate success URL

    def get_object(self, queryset=None):
        # Fetch the leader object based on the slug provided in the URL
        leader = get_object_or_404(User, slug=self.kwargs.get("slug"))
        return leader

    def get_context_data(self, **kwargs):
        # Get the default context data and add the leader profile form
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["leader_profile_form"] = LeaderProfileForm(
                self.request.POST, instance=self.object.leaderprofile
            )
        else:
            context["leader_profile_form"] = LeaderProfileForm(
                instance=self.object.leaderprofile
            )
        return context

    def form_valid(self, form):
        # Handle both the leader form and the leader profile form
        context = self.get_context_data()
        leader_profile_form = context["leader_profile_form"]

        if leader_profile_form.is_valid():
            self.object = form.save()
            leader_profile_form.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        # Re-render the form with errors if either form is invalid
        return self.render_to_response(self.get_context_data(form=form))


class PromoteView(AdminRequiredMixin, _UpdateView):
    model = LeaderProfile
    form_class = LeaderForm
    template_name = "leader/promote.html"
    success_url = reverse_lazy("leaders:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Promote"
        return context


class DeleteView(AdminRequiredMixin, _DeleteView):
    model = LeaderProfile
    template_name = "leader/confirm_delete.html"
    success_url = reverse_lazy("leader_index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action"] = "Delete"
        return context


class ShowView(_DetailView):
    model = User
    template_name = "leader/show.html"
    context_object_name = "leader"

    def get_object(self, queryset=None):
        # Fetch the leader using the slug
        leader = get_object_or_404(User, slug=self.kwargs.get("slug"))

        # Fetch the corresponding LeaderProfile if it exists
        leader_profile = getattr(leader, "leaderprofile", None)

        # You can either return a tuple or augment the leader object with the profile
        if leader_profile:
            leader.profile = leader_profile  # Attach profile to the leader object
        return leader

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Since leader_profile is now attached to the leader object, we can access it easily
        context["leader"] = self.object

        return context


class LeaderViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(user_type="leader")
    serializer_class = LeaderSerializer


class DashboardView(BaseDashboardView):
    """
    Dashboard for leaders.
    """

    template_name = "leader/dashboard.html"
    widgets = ["faction_management_widget", "reports_widget", "tasks_widget"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Example widgets data
        context["faction_management_widget"] = self.get_faction_management_data()
        context["reports_widget"] = self.get_reports_data()
        context["tasks_widget"] = self.get_tasks_data()

        return context

    def get_faction_management_data(self):
        return ["Team Member 1", "Team Member 2"]

    def get_reports_data(self):
        return ["Report 1", "Report 2"]

    def get_tasks_data(self):
        return ["Task 1", "Task 2"]
