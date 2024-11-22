# faction/urls/faction.py

from django.urls import path, include

from ..views.faction import (
    IndexView,
    IndexByOrganizationView,
    ShowView,
    CreateView,
    CreateChildView,
    UpdateView,
    DeleteView,
    ManageView,
)
from ..views.attendee import IndexByFactionView as AttendeeIndexByFactionView
from faction.views.leader import CreateView as LeaderCreateView

app_name = "factions"

urlpatterns = [
    # Index
    path("", IndexView.as_view(), name="index"),
    # Show
    path("<int:pk>", ShowView.as_view(), name="show"),
    path("<slug:slug>", ShowView.as_view(), name="show"),
    # Manage
    path("manage/", ManageView.as_view(), name="manage"),
    # Create
    path("new/", CreateView.as_view(), name="new"),
    path("<int:pk>/new", CreateChildView.as_view(), name="new_child"),
    path("<slug:slug>/new", CreateChildView.as_view(), name="new_child"),
    # Update
    path("<int:pk>/update/", UpdateView.as_view(), name="update"),
    path("<slug:slug>/update/", UpdateView.as_view(), name="update"),
    # Delete
    path("<int:pk>/delete/", DeleteView.as_view(), name="delete"),
    path("<slug:slug>/delete/", DeleteView.as_view(), name="delete"),
    # Attendees Index
    path(
        "<int:pk>/attendees/",
        AttendeeIndexByFactionView.as_view(),
        name="attendee_index_by_faction",
    ),
    path(
        "<slug:slug>/attendees/",
        AttendeeIndexByFactionView.as_view(),
        name="attendee_index_by_faction",
    ),
    path('<slug:slug>/enrollments/', include('enrollment.urls.faction', namespace='enrollments')),
    path('<slug:faction_slug>/leaders/new/', LeaderCreateView.as_view(), name="new_leader"),
]
