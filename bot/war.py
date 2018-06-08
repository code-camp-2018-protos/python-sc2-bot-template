import sc2
from sc2.constants import *

MIN_ARMY_SIZE = 9


def build_turn(iteration, id):
    return iteration % 3 == id


class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None
        self.oracle_count = 0

    async def on_step(self, iteration):
        # await self.attack_with_first_worker()
        await self.build_shitload_of_units(iteration)
        await self.attack_with_all_we_got()
        await self.move_to_defensive()
        await self.harass(iteration)

    async def move_to_defensive(self):
        """Move unit to stand between own and enemy."""
        print(self.api.enemy_start_locations[0])
        print(self.api.units(NEXUS).first.position)
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

    async def build_shitload_of_units(self, iteration):
        for unit_type, num_units in NUM_UNIT_BUILDS.items():
            await self.build_num_of(num_units, unit_type, iteration)

    async def attack_with_all_we_got(self):
        all_attacking_units = self.get_all_attacking_units()

        if len(all_attacking_units) < MIN_ARMY_SIZE:
            return

        for attacker in all_attacking_units:
            if attacker.is_idle:
                await self.api.do(attacker.attack(self.api.enemy_start_locations[0]))

    def get_all_attacking_units(self):
        units = []
        for unit_type in UNIT_BUILDER_MAP:
            for unit in self.api.units(unit_type):
                units.append(unit)
        return units


UNIT_BUILDER_MAP = {
    ZEALOT: GATEWAY,
    STALKER: GATEWAY,
    ADEPT: GATEWAY
}

NUM_UNIT_BUILDS = {
    ZEALOT: 3,
    STALKER: 10,
    ADEPT: 5
}
