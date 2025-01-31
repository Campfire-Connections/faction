# faction/forms/leader.py
"""Leader Related Forms."""

from django import forms
from user.models import User
from ..models.leader import LeaderProfile


class LeaderForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_admin"]

    def save(self, commit=True):
        leader_profile = super().save(commit=False)
        user = leader_profile.user
        user.username = self.cleaned_data["user_username"]
        user.email = self.cleaned_data["user_email"]
        user.first_name = self.cleaned_data["user_first_name"]
        user.last_name = self.cleaned_data["user_last_name"]
        if commit:
            user.save()
            leader_profile.save()
        return leader_profile


# LeaderProfile form
class LeaderProfileForm(forms.ModelForm):
    class Meta:
        model = LeaderProfile
        fields = []


class PromoteLeaderForm(forms.ModelForm):
    pass


class RegistrationForm(forms.ModelForm):
    pass
