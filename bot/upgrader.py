import sc2
from sc2.constants import *


class Upgrader():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        if iteration % 30 != 0:
            return

        for unit, dependencies in UPGRADE_TACTICS.items():
            if self.api.units(unit).empty:
                continue

            for dependency, upgrades in dependencies.items():
                if self.api.units(dependency).empty or len(upgrades) == 0:
                    continue

                first_unit = self.api.units(unit).first
                if not first_unit.is_ready:
                    continue

                first_upgrade = upgrades[0]

                if self.api.can_afford(first_upgrade):
                    print("Upgrading {} from {}".format(
                        first_upgrade, first_unit))
                    await self.api.do(first_unit(first_upgrade))
                    upgrades.remove(first_upgrade)
                    return


UPGRADE_TACTICS = {
    FORGE: {
        FORGE: [FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1, FORGERESEARCH_PROTOSSSHIELDSLEVEL1],
        TWILIGHTCOUNCIL: [FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2, FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2, FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3, FORGERESEARCH_PROTOSSSHIELDSLEVEL2, FORGERESEARCH_PROTOSSSHIELDSLEVEL3],
    },
    GATEWAY: {
        GATEWAY: [MORPH_WARPGATE]
    },
    CYBERNETICSCORE: {
        GATEWAY: [RESEARCH_WARPGATE]
        # CYBERNETICSCORE: [CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1, CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1, CYBERNETICSCORERESEARCH_RESEARCHHALLUCINATION]
    },
    TWILIGHTCOUNCIL: {
        TWILIGHTCOUNCIL: [RESEARCH_CHARGE, RESEARCH_BLINK, RESEARCH_ADEPTRESONATINGGLAIVES]
    }
}
