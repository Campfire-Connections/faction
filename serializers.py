""" Faction Model Serializers. """

from rest_framework import serializers

from .models import Faction, LeaderProfile, AttendeeProfile


class FactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faction
        fields = "__all__"


class LeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaderProfile
        fields = "__all__"


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttendeeProfile
        fields = "__all__"
