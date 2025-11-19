""" Faction Model Serializers. """

from rest_framework import serializers

from user.serializers import BaseProfileSerializer
from .models import Faction, LeaderProfile, AttendeeProfile


class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = "__all__"


class LeaderSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = LeaderProfile
        fields = BaseProfileSerializer.Meta.fields + ("faction", "organization")


class AttendeeSerializer(BaseProfileSerializer):
    class Meta(BaseProfileSerializer.Meta):
        model = AttendeeProfile
        fields = BaseProfileSerializer.Meta.fields + ("faction", "organization")
