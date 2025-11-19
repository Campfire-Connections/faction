# faction/models/attendee.py
""" Attendee Related Models. """

from django.db import models

from enrollment.models.attendee import AttendeeEnrollment
from user.models import BaseUserProfile


class AttendeeProfile(BaseUserProfile):
    class Meta:
        verbose_name = "Attendee Profile"
        verbose_name_plural = "Attendee Profiles"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_attendee_slug_per_org",
            ),
            models.UniqueConstraint(
                fields=["faction", "user"],
                name="unique_attendee_per_faction_user",
            ),
        ]

    faction = models.ForeignKey(
        "faction.Faction", on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_fallback_chain(self):
        return ["faction", "faction.organization"]

    @property
    def enrollments(self):
        """
        Dynamically fetch enrollments for this attendee.
        """
        return AttendeeEnrollment.objects.filter(attendee=self)
