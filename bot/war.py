import sc2
from sc2.constants import *

def build_turn(iteration, id):
    return iteration % 3 == id

class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None
        self.oracle_count = 0

    async def on_step(self, iteration):
        # await self.attack_with_first_worker()
        await self.build_shitload_of_zealots(iteration)
        await self.attack_with_many_zealots()
        await self.harass(iteration)

    async def move_to_defensive(self, unit):
        """Move unit to stand between own and enemy."""
        pass

    async def harass(self, iteration):
        # Gateway == Barracs
        # Janne resource ID 2

        # Check build
        if build_turn(iteration, 1) and self.api.units(STARGATE).exists:
            # Build initial Oracles
            if self.oracle_count < 2:
                for stargate in self.api.units(STARGATE).ready.noqueue:
                    if self.api.can_afford(ORACLE):
                        await self.api.do(stargate.train(ORACLE))
                        self.oracle_count += 1

        if iteration % 100 == 0:
            for oracle in self.api.units(ORACLE):
                await self.api.do(oracle.attack(self.api.enemy_start_locations[0]))


    async def build_shitload_of_zealots(self, iteration):
        if build_turn(iteration, 2):
            # Not our time
            return

        for gateway in self.api.units(GATEWAY).ready.noqueue:
            if self.api.can_afford(ZEALOT):
                await self.api.do(gateway.train(ZEALOT))

    async def attack_with_many_zealots(self):
        if len(self.api.units(ZEALOT)) > 10:
            for zealot in self.api.units(ZEALOT):
                await self.api.do(zealot.attack(self.api.enemy_start_locations[0]))
