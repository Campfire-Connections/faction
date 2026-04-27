from django.shortcuts import get_object_or_404

from enrollment.models.faction import FactionEnrollment
from enrollment.tables.faction import FactionEnrollmentTable
from faction.models.attendee import AttendeeProfile
from faction.models.faction import Faction
from faction.models.leader import LeaderProfile
from faction.tables.attendee import AttendeeTable
from faction.tables.faction import ChildFactionTable, FactionTable
from faction.tables.leader import LeaderTable


def active_factions():
    return Faction.objects.filter(is_deleted=False).select_related(
        "organization", "parent"
    )


def get_active_faction_by_slug(slug):
    return get_object_or_404(Faction, slug=slug, is_deleted=False)


def get_active_faction_by_id(faction_id):
    return get_object_or_404(Faction, id=faction_id, is_deleted=False)


def faction_descendant_ids(faction):
    ids = []
    stack = [faction]
    while stack:
        current = stack.pop()
        ids.append(current.id)
        stack.extend(list(current.children.all()))
    return ids


def leaders_for_faction(faction):
    return LeaderProfile.objects.filter(faction=faction).select_related("user")


def attendees_for_faction_tree(faction):
    return AttendeeProfile.objects.filter(
        faction_id__in=faction_descendant_ids(faction)
    ).select_related("user")


def roster_for_faction_tree(faction):
    faction_ids = faction_descendant_ids(faction)
    leaders_qs = LeaderProfile.objects.filter(
        faction_id__in=faction_ids
    ).select_related("user", "organization", "faction")
    attendees_qs = AttendeeProfile.objects.filter(
        faction_id__in=faction_ids
    ).select_related("user", "organization", "faction")
    return list(leaders_qs) + list(attendees_qs)


def child_factions_for_faction(faction):
    return Faction.objects.filter(parent=faction, is_deleted=False)


def enrollments_for_faction(faction):
    return FactionEnrollment.objects.filter(faction=faction)


def faction_manage_tables_config(faction):
    context = {"faction_slug": faction.slug}
    return {
        "leaders": {
            "class": LeaderTable,
            "queryset": leaders_for_faction(faction),
            "context": context,
        },
        "attendees": {
            "class": AttendeeTable,
            "queryset": attendees_for_faction_tree(faction),
            "context": context,
        },
        "enrollments": {
            "class": FactionEnrollmentTable,
            "queryset": enrollments_for_faction(faction),
            "context": context,
        },
        "child_factions": {
            "class": ChildFactionTable,
            "queryset": child_factions_for_faction(faction),
            "context": context,
        },
    }


def faction_index_table_config():
    return {
        "class": FactionTable,
        "queryset": active_factions().order_by("name"),
    }
