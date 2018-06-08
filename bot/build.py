import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.ids.buff_id import BuffId

DESIRED_WORKER_COUNT = 16

class Build():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        if not self.api.units(NEXUS).exists:
            #print("Nexus gone, nope build")
            return
        else:
            nexus = self.api.units(NEXUS).first

        # Mine minerals biatch
        for idle_worker in self.api.workers.idle:
            mf = self.api.state.mineral_field.closest_to(idle_worker)
            await self.api.do(idle_worker.gather(mf))    

        # Create new workers first
        if self.api.workers.amount < DESIRED_WORKER_COUNT and nexus.noqueue:
            if self.api.can_afford(PROBE):
                print("Train new worker")
                await self.api.do(nexus.train(PROBE))
            else:
                print("Can't afford worker")

        await self.build_gas_stuff()

        #print("Build step done")

    async def build_gas_stuff(self):
        for nexus in self.api.units(NEXUS).ready:
            vgs = self.api.state.vespene_geyser.closer_than(20.0, nexus)
            for vg in vgs:
                if not self.api.can_afford(ASSIMILATOR):
                    #print("Can't afford assimilator")
                    break

                worker = self.api.select_build_worker(vg.position)
                if worker is None:
                    #print("Can't find worker for building assimilator")
                    break

                if not self.api.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                    print("Build gas assimilator")
                    await self.api.do(worker.build(ASSIMILATOR, vg))
