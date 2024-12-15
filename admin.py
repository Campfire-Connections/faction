# faction/admin.py

from django.contrib import admin

from .models.faction import Faction
from .models.leader import LeaderProfile
from .models.attendee import AttendeeProfile

admin.site.register(Faction)
admin.site.register(LeaderProfile)
admin.site.register(AttendeeProfile)
