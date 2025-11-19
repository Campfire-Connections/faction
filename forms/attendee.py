# faction/forms/attendee.py
"""Attendee Related Forms."""

from django import forms

from user.forms import ProfileUserFieldsMixin
from ..models.attendee import AttendeeProfile


class AttendeeProfileForm(forms.ModelForm):
    class Meta:
        model = AttendeeProfile
        fields = []


class AttendeeForm(ProfileUserFieldsMixin):
    class Meta:
        model = AttendeeProfile
        fields = []

class PromoteAttendeeForm(forms.ModelForm):
    pass

class RegistrationForm(forms.ModelForm):
    pass
