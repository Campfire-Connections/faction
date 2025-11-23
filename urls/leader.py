# faction/urls/leader.py

from django.urls import path, include
from faction.views.leader import (
    IndexView,
    CreateView,
    ShowView,
    UpdateView,
    DeleteView,
    PromoteView,
    ManageView,
    DashboardView,
)

app_name = "leaders"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("new/", CreateView.as_view(), name="new"),
    # Dashboard
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("<slug:slug>/", ShowView.as_view(), name="show"),
    path("<slug:slug>/edit/", UpdateView.as_view(), name="edit"),
    path("<slug:slug>/delete/", DeleteView.as_view(), name="delete"),
    path("<slug:slug>/promote/", PromoteView.as_view(), name="promote"),
    path("manage/", ManageView.as_view(), name="manage"),
    path('<slug:slug>/enrollments/', include('enrollment.urls.leader', namespace='enrollments')),
    
]
