# faction/forms/attendee.py
"""Attendee Related Forms."""

from django import forms

from user.forms import ProfileUserFieldsMixin
from ..models.attendee import AttendeeProfile
from faction.models.faction import Faction


class AttendeeProfileForm(forms.ModelForm):
    class Meta:
        model = AttendeeProfile
        fields = []


class AttendeeForm(ProfileUserFieldsMixin):
    """
    Capture attendee user info plus faction assignment.
    """

    faction = forms.ModelChoiceField(
        queryset=Faction.objects.none(),
        required=True,
        label="Faction",
        help_text="Assign the attendee to a faction or sub-faction.",
    )

    def __init__(self, *args, scope_faction=None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = Faction.objects.filter(is_deleted=False)
        if scope_faction:
            # limit to the scope faction and its descendants
            ids = []
            stack = [scope_faction]
            while stack:
                current = stack.pop()
                ids.append(current.id)
                stack.extend(list(current.children.all()))
            qs = qs.filter(id__in=ids)
        self.fields["faction"].queryset = qs

    class Meta:
        model = AttendeeProfile
        fields = ["faction"]

class PromoteAttendeeForm(forms.ModelForm):
    pass

class RegistrationForm(forms.ModelForm):
    pass
