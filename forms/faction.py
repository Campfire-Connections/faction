""" Faction Related Forms. """

from django import forms
from django.core.exceptions import ValidationError
from ..models.faction import Faction


class FactionForm(forms.ModelForm):
    class Meta:
        model = Faction
        fields = ["name", "description", "organization"]

    def __init__(self, *args, **kwargs):
        super(FactionForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter faction name"}
        )
        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Describe the faction"}
        )

    def clean(self):
        cleaned_data = super().clean()

        # Access settings using the new get_setting() method from SettingsMixin
        organization = cleaned_data.get('organization')
        if organization:
            max_faction_depth = organization.get_setting('max_faction_depth', default=2)
            if self.instance.get_depth() > max_faction_depth:
                raise ValidationError(f"Max faction depth exceeded for organization '{organization.name}'.")
        
        return cleaned_data


class ChildFactionForm(forms.ModelForm):
    class Meta:
        model = Faction
        fields = ["name", "description", "parent", "organization"]

    def __init__(self, *args, **kwargs):
        super(ChildFactionForm, self).__init__(*args, **kwargs)
        # Customize widgets for better user experience
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Enter child faction name"}
        )
        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Describe the child faction"}
        )
        # Parent and organization fields should be hidden since they are handled automatically
        self.fields["parent"].widget = forms.HiddenInput()
        self.fields["organization"].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()

        parent = self.cleaned_data.get('parent') or self.instance.parent
        if not parent:
            raise ValidationError("Parent faction must be set.")

        # Access the organization's settings via the parent using the get_setting method
        organization = parent.organization
        if not organization:
            raise ValidationError("Parent faction must be associated with an organization.")
        
        # Access settings from the organization through the SettingsMixin
        max_faction_depth = organization.get_setting('max_faction_depth', default=2)
        if parent.get_depth() >= max_faction_depth:
            raise ValidationError(f"Max faction depth of {max_faction_depth} exceeded for organization '{organization.name}'.")

        # You can also handle additional settings, like attendee limits
        max_attendees = organization.get_setting('max_attendees_per_faction', default=50)
        # Validate attendee-related logic, if needed

        return cleaned_data
