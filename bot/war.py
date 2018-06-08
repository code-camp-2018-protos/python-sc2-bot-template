import sc2
from sc2.constants import *


class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None

    async def on_step(self, iteration):
        #first_nexus = self.api.units(NEXUS).ready.first
        if self.api.workers.find_by_tag(self.first_worker_tag) is None:
            self.first_worker_tag = self.api.workers.first.tag

        first_worker = self.api.workers.find_by_tag(self.first_worker_tag)

        await self.api.do(first_worker.attack(self.api.enemy_start_locations[0]))
