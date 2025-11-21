# Faction App

The `faction` app manages the units that attend facilities (patrols, crews, squads) along with
their leader and attendee profiles.

## Responsibilities

- `Faction` model (hierarchical, addressable) plus relationships to organizations.
- Profile models for leaders and attendees with unique constraints per organization/faction.
- CRUD views, tables, and DRF viewsets for both leaders and attendees.
- Portal dashboards for faction leaders and attendees, wired into the shared widget system.
- Forms for promotions, registrations, and roster management.

## Highlights

- Scoped mixins (`FactionScopedMixin`) keep views filtered to the active faction context and
  ensure portal permissions are honored.
- Tables/forms operate directly on profile models, keeping user-specific fields and portal data
  centralized.
- View classes reuse the shared base views so they automatically gain breadcrumb, action,
  and widget support.

## Tests

```bash
python manage.py test faction
```

Extend these tests whenever you add roster rules or additional faction-side widgets.
