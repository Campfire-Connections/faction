# faction/urls/faction.py

from django.urls import path, include

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
    path("manage/", ManageView.as_view(), name="manage"),
    path("new/", CreateView.as_view(), name="new"),
    path("<slug:slug>", ShowView.as_view(), name="show"),
    path("<slug:slug>/new", CreateChildView.as_view(), name="new_child"),
    path("<slug:slug>/roster/", RosterView.as_view(), name="roster"),
    path("<slug:slug>/update/", UpdateView.as_view(), name="update"),
    path("<slug:slug>/delete/", DeleteView.as_view(), name="delete"),
    path(
        "<slug:slug>/attendees/",
        include("faction.urls.attendee", namespace="attendees"),
    ),
    path(
        "<slug:slug>/enrollments/",
        include("enrollment.urls.faction", namespace="enrollments"),
    ),
    path(
        "<slug:faction_slug>/leaders",
        include("faction.urls.leader", namespace="leaders"),
    ),
]
