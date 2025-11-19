# faction/forms/leader.py
"""Leader Related Forms."""

from django import forms

from user.forms import ProfileUserFieldsMixin
from ..models.leader import LeaderProfile


class LeaderForm(ProfileUserFieldsMixin):
    class Meta:
        model = LeaderProfile
        fields = []


# LeaderProfile form
class LeaderProfileForm(forms.ModelForm):
    class Meta:
        model = LeaderProfile
        fields = []


class PromoteLeaderForm(forms.ModelForm):
    pass


class RegistrationForm(forms.ModelForm):
    pass
