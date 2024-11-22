# faction/urls/__init__.py

from django.urls import path, include

urlpatterns = [
    path('factions/', include('faction.urls.faction')),
    path('attendees/', include('faction.urls.attendee')),
    path('leaders/', include('faction.urls.leader')),
]
