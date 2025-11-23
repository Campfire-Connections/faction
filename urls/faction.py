# faction/urls/faction.py

from django.urls import path, include

from enrollment.views.faction import FactionEnrollmentIndexView
from faction.views.faction import (
    IndexView,
    ShowView,
    CreateView,
    CreateChildView,
    UpdateView,
    DeleteView,
    ManageView,
    RosterView,
)


app_name = "factions"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("<slug:faction_slug>/manage/", ManageView.as_view(), name="manage"),
    path("new/", CreateView.as_view(), name="new"),
    path("<slug:faction_slug>", ShowView.as_view(), name="show"),
    path("<slug:faction_slug>/<slug:child_slug>/", ShowView.as_view(), name="show_child"),
    path("<slug:faction_slug>/new", CreateChildView.as_view(), name="new_child"),
    path("<slug:faction_slug>/roster/", RosterView.as_view(), name="roster"),
    path("<slug:faction_slug>/update/", UpdateView.as_view(), name="update"),
    path("<slug:faction_slug>/delete/", DeleteView.as_view(), name="delete"),
    path(
        "<slug:faction_slug>/attendees/",
        include("faction.urls.attendee", namespace="attendees"),
    ),
    path(
        "<slug:faction_slug>/enrollments/",
        include("enrollment.urls.faction", namespace="enrollments"),
    ),
    path(
        "<slug:faction_slug>/enrollments", FactionEnrollmentIndexView.as_view(),
        name="enrollments_index"),
    path(
        "<slug:faction_slug>/leaders/",
        include("faction.urls.leader", namespace="leaders"),
    ),
]
