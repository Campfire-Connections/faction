# faction/models/leader.py
""" Leader Related Models. """

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User, BaseUserProfile


class LeaderProfile(BaseUserProfile):
    class Meta:
        verbose_name = "Leader"
        verbose_name_plural = "Leaders"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "slug"],
                name="unique_leader_slug_per_org",
            ),
            models.UniqueConstraint(
                fields=["faction", "user"],
                name="unique_leader_per_faction_user",
            ),
        ]

    is_admin = models.BooleanField(default=False)
    faction = models.ForeignKey(
        "faction.Faction", on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_fallback_chain(self):
        return ["faction", "faction.organization"]

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("leaders:show", kwargs={"slug": self.slug})
