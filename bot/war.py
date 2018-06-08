import sc2
from sc2.constants import *

def build_turn(iteration, id):
    return iteration % 3 == id

class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None

    async def on_step(self, iteration):
        # await self.attack_with_first_worker()
        await self.build_shitload_of_zealots(iteration)
        await self.build_shitload_of_stalkers(iteration)
        await self.attack_with_all_we_got()

    async def attack_with_first_worker(self):
        if self.api.workers.find_by_tag(self.first_worker_tag) is None:
            self.first_worker_tag = self.api.workers.first.tag

        first_worker = self.api.workers.find_by_tag(self.first_worker_tag)

        await self.api.do(first_worker.attack(self.api.enemy_start_locations[0]))

    async def build_num_of(self, number_of_units, unit_type, iteration):
        if build_turn(iteration, 2):
            # Not our time
            return

        if unit_type not in UNIT_BUILDER_MAP:
            #print unit_type + ' not defined!!!!'
            pass

        if len(self.api.units(unit_type)) < number_of_units:
            for building_unit in self.api.units(UNIT_BUILDER_MAP[unit_type]).ready.noqueue:
                if self.api.can_afford(unit_type):
                    await self.api.do(building_unit.train(unit_type))

    async def build_shitload_of_zealots(self, iteration):
        await self.build_num_of(3, ZEALOT, iteration)

    async def build_shitload_of_stalkers(self, iteration):
        await self.build_num_of(10, STALKER, iteration)

    async def attack_with_all_we_got(self):
        if len(self.api.units(ZEALOT)) >= 3 and len(self.api.units(STALKER)) >= 10:
            for zealot in self.api.units(ZEALOT):
                await self.api.do(zealot.attack(self.api.enemy_start_locations[0]))
            for stalker in self.api.units(STALKER):
                await self.api.do(stalker.attack(self.api.enemy_start_locations[0]))


UNIT_BUILDER_MAP = {
    ZEALOT: GATEWAY,
    STALKER: GATEWAY
}
