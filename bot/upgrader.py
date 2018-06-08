import sc2
from sc2.constants import *


class Upgrader():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        for unit, upgrades in UPGRADE_TACTICS.items():
            if self.api.units(unit).empty or len(upgrades) == 0:
                continue

            first_unit = self.api.units(unit).first
            if not first_unit.is_ready:
                continue

            first_upgrade = upgrades[0]

            if self.api.can_afford(first_upgrade):
                await self.api.do(first_unit(first_upgrade))
                upgrades.remove(first_upgrade)
                return


UPGRADE_TACTICS = {
    FORGE: [FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, FORGERESEARCH_PROTOSSSHIELDSLEVEL1],
    CYBERNETICSCORE: [CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1, CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1, CYBERNETICSCORERESEARCH_RESEARCHHALLUCINATION],
    TWILIGHTCOUNCIL: []
}
