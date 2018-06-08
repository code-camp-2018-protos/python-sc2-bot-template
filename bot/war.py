import sc2
from sc2.constants import *


class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None

    async def on_step(self, iteration):
        await self.attack_with_first_worker()
        await self.build_shitload_of_zealots(iteration)
        await self.attack_with_many_zealots()

    async def attack_with_first_worker(self):
        if self.api.workers.find_by_tag(self.first_worker_tag) is None:
            self.first_worker_tag = self.api.workers.first.tag

        first_worker = self.api.workers.find_by_tag(self.first_worker_tag)

        await self.api.do(first_worker.attack(self.api.enemy_start_locations[0]))

    async def build_shitload_of_zealots(self, iteration):
        if iteration % 3 != 2:
            # Not our time
            return

        for gateway in self.api.units(GATEWAY).ready.noqueue:
            if self.api.can_afford(ZEALOT):
                await self.api.do(gateway.train(ZEALOT))

    async def attack_with_many_zealots(self):
        if len(self.api.units(ZEALOT)) > 10:
            for zealot in self.api.units(ZEALOT):
                await self.api.do(zealot.attack(self.api.enemy_start_locations[0]))
