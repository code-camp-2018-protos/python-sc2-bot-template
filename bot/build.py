import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.ids.buff_id import BuffId
from sc2.position import Point2

DESIRED_WORKER_COUNT = 16
DESIRED_GATEWAY_COUNT = 2
DESIRED_STARGATE_COUNT = 2
DESIRED_CANNON_COUNT = 2

class Build():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        if not self.api.units(NEXUS).exists:
            #print("Nexus gone, nope build")
            return
        else:
            nexus = self.api.units(NEXUS).first

        if iteration == 1:
            self.cannon_positions = [
                Point2((max({p.x for p in d}), min({p.y for p in d})))
                for d in self.api.main_base_ramp.top_wall_depos
            ]

        await self.train_new_workers(nexus)
        await self.build_pylons(nexus)
        await self.build_gas_stuff()
        await self.build_gateway(nexus)
        await self.build_cybernetics_core()
        await self.build_stargate(nexus, iteration)
        await self.build_forge()
        await self.manage_workers(nexus)
        await self.build_cannons(nexus, iteration)
        await self.build_twilight_cauncil()

        #print("Build step done")

    async def manage_workers(self, nexus):
        # Mine minerals biatch

        def find_empty_gasfield():
            for g in self.api.geysers:
                if g.ideal_harvesters > g.assigned_harvesters:
                    return g

        for idle_worker in self.api.workers.idle:
            empty_gasfield = find_empty_gasfield()
            if empty_gasfield:
                #print("Assign worker to gasfield", idle_worker.tag)
                await self.api.do(idle_worker.gather(empty_gasfield))
            else:
                mf = self.api.state.mineral_field.closest_to(idle_worker)
                #print("Assign worker to mineral field", idle_worker.tag)
                await self.api.do(idle_worker.gather(mf))

        #await self.api.distribute_workers()

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
                await self.api.build(PYLON, near=self.build_position(nexus))
        elif self.api.supply_left < 2 and not self.api.already_pending(PYLON):
            if self.api.can_afford(PYLON):
                print("Building additional pylon")
                await self.api.build(PYLON, near=self.build_position(nexus))

    async def build_gas_stuff(self):
        def gaysers_not_full():
            for g in self.api.geysers:
                if g.ideal_harvesters > g.assigned_harvesters:
                    return True
            return False

        for nexus in self.api.units(NEXUS).ready:
            vgs = self.api.state.vespene_geyser.closer_than(20.0, nexus)
            should_not_build = gaysers_not_full()
            if self.api.units(ASSIMILATOR).ready.exists and (should_not_build or not self.api.units(STARGATE).ready.exists):
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

    async def build_gateway(self, nexus):
        if not self.api.units(PYLON).ready.exists:
            return
        
        if self.api.units(GATEWAY).amount < DESIRED_GATEWAY_COUNT:
            if self.api.can_afford(GATEWAY) and not self.api.already_pending(GATEWAY):
                print("Build gateway")
                await self.api.build(GATEWAY, near=self.build_position(nexus))

    async def build_cybernetics_core(self):
        if self.api.units(GATEWAY).ready.exists and not self.api.units(CYBERNETICSCORE).exists:
            pylon = self.api.units(PYLON).ready.random
            if self.api.can_afford(CYBERNETICSCORE) and not self.api.already_pending(CYBERNETICSCORE):
                print("Build cybernetics core")
                await self.api.build(CYBERNETICSCORE, near=pylon)

    async def build_stargate(self, nexus, iteration):
        if not self.api.units(PYLON).ready.exists or not self.api.units(CYBERNETICSCORE).ready.exists:
            return
        
        if self.api.units(STARGATE).amount < DESIRED_STARGATE_COUNT and not self.api.already_pending(STARGATE):
            if (not self.api.units(STARGATE).ready.exists or iteration > 1100) and self.api.can_afford(STARGATE):
                print("Build stargate")
                await self.api.build(STARGATE, near=self.build_position(nexus))
    
    async def build_forge(self):
        if not self.api.units(PYLON).ready.exists or self.api.units(FORGE).ready.exists:
            return
        pylon = self.api.units(PYLON).ready.random
        if not self.api.already_pending(FORGE):
            if self.api.can_afford(FORGE):
                print("Build forge")
                await self.api.build(FORGE, near=pylon)

    async def build_twilight_cauncil(self):
        if self.api.units(STARGATE).amount < DESIRED_STARGATE_COUNT or self.api.units(TWILIGHTCOUNCIL).ready.exists:
            return
        pylon = self.api.units(PYLON).ready.random
        if not self.api.already_pending(TWILIGHTCOUNCIL) and self.api.can_afford(TWILIGHTCOUNCIL):
            print("Build twilight council")
            await self.api.build(TWILIGHTCOUNCIL, near=pylon)

    async def build_cannons(self, nexus, iteration):
        cannon_count = self.api.units(PHOTONCANNON).amount
        if self.api.units(STARGATE).ready.exists and cannon_count < DESIRED_CANNON_COUNT and not self.api.already_pending(PHOTONCANNON):
            if self.api.can_afford(PHOTONCANNON) and iteration % 10 == 0:
                print("Building cannon")
                desired_cannon_position = list(self.cannon_positions)[cannon_count]
                await self.api.build(PHOTONCANNON, near=desired_cannon_position, max_distance=10)

    def build_position(self, nexus):
        distance = (self.api.units(PYLON).amount * 4) + 5
        return nexus.position.towards_with_random_angle(self.api.game_info.map_center, distance)
