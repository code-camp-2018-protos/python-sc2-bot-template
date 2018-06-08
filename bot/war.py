import sc2
from sc2.constants import *

def can_afford(iteration, id):
    return iteration % 3 == id

class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None

    async def on_step(self, iteration):
        #first_nexus = self.api.units(NEXUS).ready.first
        await self.harass(iteration)

    async def harass(self, iteration):
        # Gateway == Barracs
        # Janne resource ID 2

        # Check build
        if can_afford(iteration, 2) and self.api.units(STARGATE).exists:
            # Build initial Oracles
            if self.api.units(ORACLE).amount < 2 and self.api.can_afford(ORACLE):
                await self.api.build(ORACLE)

        for oracle in self.api.units(ORACLE):
            await self.do(oracle.move(self.enemy_start_locations[0]))


    async def attack_with_first_worker(self):
        if self.api.workers.find_by_tag(self.first_worker_tag) is None:
            self.first_worker_tag = self.api.workers.first.tag

        first_worker = self.api.workers.find_by_tag(self.first_worker_tag)

        await self.api.do(first_worker.attack(self.api.enemy_start_locations[0]))
