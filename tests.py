from core.tests import BaseDomainTestCase
from faction.models import Faction


class FactionModelTests(BaseDomainTestCase):
    def test_get_root_faction_returns_top_parent(self):
        child = Faction.objects.create(
            name="Eagle Patrol - Bravo",
            organization=self.organization,
            parent=self.faction,
        )

        self.assertEqual(child.get_root_faction(), self.faction)
