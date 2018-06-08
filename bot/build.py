import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.ids.buff_id import BuffId

DESIRED_WORKER_COUNT = 16
DESIRED_STARGATE_COUNT = 2

class Build():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        if not self.api.units(NEXUS).exists:
            #print("Nexus gone, nope build")
            return
        else:
            nexus = self.api.units(NEXUS).first

        await self.train_new_workers(nexus)
        await self.build_gas_stuff()
        await self.build_pylons(nexus)
        await self.build_gateway()
        await self.build_cybernetics_core()
        await self.build_stargate()
        await self.manage_workers(nexus)

        #print("Build step done")

    async def manage_workers(self, nexus):
        # Mine minerals biatch
        await self.api.distribute_workers()
        #for idle_worker in self.api.workers.idle:
        #    mf = self.api.state.mineral_field.closest_to(idle_worker)
        #    await self.api.do(idle_worker.gather(mf))

    async def train_new_workers(self, nexus):
        if self.api.workers.amount < DESIRED_WORKER_COUNT and nexus.noqueue:
            if self.api.can_afford(PROBE):
                print("Train new worker")
                await self.api.do(nexus.train(PROBE))

    async def build_pylons(self, nexus):
        if self.api.already_pending(PYLON):
            return
        if not self.api.units(PYLON).exists:
            if self.api.can_afford(PYLON):
                print("Building first pylon!")
                await self.api.build(PYLON, near=nexus)
        elif self.api.supply_left < 2 and not self.api.already_pending(PYLON):
            if self.api.can_afford(PYLON):
                print("Building additional pylon")
                await self.api.build(PYLON, near=nexus)

    async def build_gas_stuff(self):
        def gaysers_not_full():
            for g in self.api.geysers:
                if g.ideal_harvesters > g.assigned_harvesters:
                    return True
            return False

        for nexus in self.api.units(NEXUS).ready:
            vgs = self.api.state.vespene_geyser.closer_than(20.0, nexus)
            should_build = gaysers_not_full()
            if self.api.units(ASSIMILATOR).ready.exists and not should_build:
                return
            for vg in vgs:
                if self.api.already_pending(ASSIMILATOR):
                    return
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

    async def build_gateway(self):
        if not self.api.units(PYLON).ready.exists:
            return
        
        pylon = self.api.units(PYLON).ready.random
        if not self.api.units(GATEWAY).ready.exists:
            if self.api.can_afford(GATEWAY) and not self.api.already_pending(GATEWAY):
                print("Build gateway")
                await self.api.build(GATEWAY, near=pylon)

    async def build_cybernetics_core(self):
        if self.api.units(GATEWAY).ready.exists and not self.api.units(CYBERNETICSCORE).exists:
            pylon = self.api.units(PYLON).ready.random
            if self.api.can_afford(CYBERNETICSCORE) and not self.api.already_pending(CYBERNETICSCORE):
                print("Build cybernetics core")
                await self.api.build(CYBERNETICSCORE, near=pylon)

    async def build_stargate(self):
        if not self.api.units(PYLON).ready.exists or not self.api.units(CYBERNETICSCORE).ready.exists:
            return
        
        pylon = self.api.units(PYLON).ready.random
        if self.api.units(STARGATE).amount < DESIRED_STARGATE_COUNT and not self.api.already_pending(STARGATE):
            if self.api.can_afford(STARGATE):
                print("Build stargate")
                await self.api.build(STARGATE, near=pylon)

