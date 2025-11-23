# faction/forms/leader.py
"""Leader Related Forms."""

from django import forms

from user.forms import ProfileUserFieldsMixin
from ..models.leader import LeaderProfile


class LeaderForm(ProfileUserFieldsMixin):
    class Meta:
        model = LeaderProfile
        fields = ["is_admin"]
        widgets = {
            "is_admin": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


# LeaderProfile form
class LeaderProfileForm(forms.ModelForm):
    class Meta:
        model = LeaderProfile
        fields = ["is_admin"]
        widgets = {
            "is_admin": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class PromoteLeaderForm(forms.ModelForm):
    class Meta:
        model = LeaderProfile
        fields = ["is_admin"]
        widgets = {
            "is_admin": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class RegistrationForm(forms.ModelForm):
    pass

class QuartersAssignmentForm(forms.Form):
    """
    Placeholder: Leader assigning quarters (housing) to themselves or sub-leaders.
    You will later extend this to reference actual Quarters models.
    """
    quarters = forms.CharField(required=True)