# faction/models/leader.py
""" Leader Related Models. """

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from user.models import User, BaseUserProfile


class LeaderProfile(BaseUserProfile):
    class Meta:
        verbose_name = "Leader Profile"
        verbose_name_plural = "Leader Profiles"

    faction = models.ForeignKey(
        "faction.Faction", on_delete=models.SET_NULL, null=True, blank=True
    )

    def get_fallback_chain(self):
        return ["faction", "faction.organization"]
