from math import pi
import sc2
from sc2 import Race, Difficulty
from sc2.constants import *
from sc2.player import Bot, Computer
from sc2.ids.buff_id import BuffId
from sc2.position import Point2

DESIRED_WORKER_COUNT = 20
DESIRED_GATEWAY_COUNT = 2
DESIRED_STARGATE_COUNT = 2
DESIRED_CANNON_COUNT = 2
DESIRED_NEXUS_COUNT = 2
DESIRED_FREE_SUPPLY = 5


class Build():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        if iteration == 1:
            self.cannon_positions = [
                Point2((max({p.x for p in d}), min({p.y for p in d})))
                for d in self.api.main_base_ramp.top_wall_depos
            ]

        for nexus in self.api.units(NEXUS).ready:
            await self.train_new_workers(nexus)
            await self.build_pylons(nexus)
            await self.build_gateway(nexus)
            await self.build_stargate(nexus, iteration)
            await self.manage_workers(nexus, iteration)
            await self.build_cannons(nexus, iteration)

        await self.build_gas_stuff()
        await self.build_cybernetics_core()
        await self.build_forge()
        await self.build_twilight_cauncil()
        await self.expanse(iteration)

    async def expanse(self, iteration):
        if iteration > 200 and self.api.units(NEXUS).amount < DESIRED_NEXUS_COUNT and self.api.units(STARGATE).exists:
            if self.api.can_afford(NEXUS):
                print("Expanse!")
                await self.api.expand_now()
                # expansion_position = await self.api.get_next_expansion()
                # await self.api.build(NEXUS, near=expansion_position)

    async def manage_workers(self, nexus, iteration):
        # Mine minerals biatch
        if iteration % 10 != 0:
            return

        if iteration % 18 == 0:
            await self.api.distribute_workers()
            return

        def find_empty_gasfield():
            for g in self.api.geysers:
                if g.ideal_harvesters > g.assigned_harvesters:
                    return g

        for idle_worker in self.api.workers.idle:
            empty_gasfield = find_empty_gasfield()
            if empty_gasfield:
                await self.api.do(idle_worker.gather(empty_gasfield))

    async def train_new_workers(self, nexus):
        if self.api.workers.amount < (DESIRED_WORKER_COUNT*self.api.units(NEXUS).amount) and nexus.noqueue:
            if self.api.can_afford(PROBE):
                print("Train new worker")
                await self.api.do(nexus.train(PROBE))

    async def build_pylons(self, nexus):
        if self.api.already_pending(PYLON):
            return
        if not self.api.units(PYLON).exists:
            if self.api.can_afford(PYLON):
                print("Building first pylon!")
                await self.api.build(PYLON, near=self.safe_base_build_position(nexus))
        elif self.api.supply_left < DESIRED_FREE_SUPPLY and not self.api.already_pending(PYLON):
            if self.api.can_afford(PYLON):
                print("Building additional pylon")
                await self.api.build(PYLON, near=self.safe_base_build_position(nexus))

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
                if self.api.already_pending(ASSIMILATOR) or not self.api.can_afford(ASSIMILATOR):
                    break

                worker = self.api.select_build_worker(vg.position)
                if worker is None:
                    break

                if not self.api.units(ASSIMILATOR).closer_than(1.0, vg).exists:
                    print("Build gas assimilator ",
                          self.api.units(ASSIMILATOR).amount+1)
                    await self.api.do(worker.build(ASSIMILATOR, vg))

    def has_gateways(self):
        return self.api.units(GATEWAY).amount >= (DESIRED_GATEWAY_COUNT * self.api.units(NEXUS).amount)

    async def build_gateway(self, nexus):
        if not self.api.units(PYLON).ready.exists:
            return

        if not self.has_gateways():
            if self.api.can_afford(GATEWAY) and not self.api.already_pending(GATEWAY):
                pylon = self.api.units(PYLON).ready.random
                print("Build gateway ", self.api.units(GATEWAY).amount+1)
                await self.api.build(GATEWAY, near=pylon)

    async def build_cybernetics_core(self):
        if self.has_gateways() and not self.api.units(CYBERNETICSCORE).exists:
            if self.api.units(PYLON).ready.empty:
                return
            pylon = self.api.units(PYLON).ready.random
            if self.api.can_afford(CYBERNETICSCORE) and not self.api.already_pending(CYBERNETICSCORE):
                print("Build cybernetics core")
                await self.api.build(CYBERNETICSCORE, near=pylon)

    async def build_stargate(self, nexus, iteration):
        if not self.api.units(PYLON).ready.exists or not self.api.units(CYBERNETICSCORE).ready.exists:
            return

        if self.api.units(STARGATE).amount < DESIRED_STARGATE_COUNT and not self.api.already_pending(STARGATE):
            if self.api.can_afford(STARGATE):
                print("Build stargate ", self.api.units(STARGATE).amount+1)
                pylon = self.api.units(PYLON).ready.random
                await self.api.build(STARGATE, near=pylon)

    async def build_forge(self):
        if self.api.units(FORGE).ready.exists or not self.api.units(STARGATE).exists:
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
        cannon_count = self.api.units(
            PHOTONCANNON).amount * self.api.units(NEXUS).amount
        if self.api.units(STARGATE).ready.exists and cannon_count < DESIRED_CANNON_COUNT and not self.api.already_pending(PHOTONCANNON):
            if self.api.can_afford(PHOTONCANNON) and iteration % 10 == 0:
                print("Building cannon", self.api.units(PHOTONCANNON).amount+1)
                desired_cannon_position = list(
                    self.cannon_positions)[cannon_count]
                await self.api.build(PHOTONCANNON, near=desired_cannon_position, max_distance=10)

    def safe_base_build_position(self, nexus):
        distance = min(((self.api.units(PYLON).amount * 4) + 5), 18)
        return nexus.position.towards_with_random_angle(self.api.game_info.map_center, distance, (pi/2))
