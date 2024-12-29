# faction/urls/attendee.py

from django.urls import path, include
from faction.views.attendee import (
    IndexView,
    CreateView,
    ShowView,
    UpdateView,
    DeleteView,
    PromoteView,
    ManageView,
    DashboardView,
)

app_name = "attendees"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", CreateView.as_view(), name="new"),
    path("<int:pk>/", ShowView.as_view(), name="show"),
    path("<slug:slug>/", ShowView.as_view(), name="show"),
    path("<int:pk>/edit/", UpdateView.as_view(), name="edit"),
    path("<slug:slug>/edit/", UpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", DeleteView.as_view(), name="delete"),
    path("<slug:slug>/delete/", DeleteView.as_view(), name="delete"),
    path("<int:pk>/promote/", PromoteView.as_view(), name="promote"),
    path("<slug:slug>/promote/", PromoteView.as_view(), name="promote"),
    path("manage/", ManageView.as_view(), name="manage"),
    path("enrollments/", include("enrollment.urls.attendee", namespace="enrollment")),
    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
