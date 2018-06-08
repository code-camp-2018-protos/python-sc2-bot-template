import sc2
from sc2.constants import *
from sc2.position import Point2
import time

MIN_ARMY_SIZE = 9
ORACLE_HARASS = 0


def build_turn(iteration, id):
    return iteration % 3 == id


class War():
    def __init__(self, api):
        self.api = api
        self.first_worker_tag = None
        self.oracle_count = 0
        self.home_ramp_location = None
        self.unit_healths = {}  # Tag, Health

    async def on_step(self, iteration):
        # await self.attack_with_first_worker()

        if iteration == 0:
            self.home_ramp_location = [
                Point2((max({p.x for p in d}), min({p.y for p in d})))
                for d in self.api.main_base_ramp.top_wall_depos
            ][0]

        if self.oracle_count >= ORACLE_HARASS:
            await self.build_shitload_of_units(iteration)
        await self.attack_with_all_we_got()
        await self.move_to_defensive(iteration, list(UNIT_BUILDER_MAP.keys()))
        await self.harass(iteration)

    async def on_start(self):
        pass

    async def move_to_defensive(self, iteration, units):
        """Move unit to stand between own and enemy.
        Priotise saving units over watching the ramp.
        """

        units_under_attack = self.units_under_attack()

        # Check if empty
        if units_under_attack:
            pass
            # for unit_type in units:
            #    by_type = self.get_all_units_by_type(unit_type)
            #    for unit in by_type:
            #        if unit.is_idle:
            #            await self.api.do(unit.move(self.api.units(unit_type).find_by_tag(units_under_attack[0]).location))
        else:
            if iteration % 10 == 0:
                start = time.time()
                for unittype in units:
                    far_from_ramp = self.api.units(
                        unittype) - self.api.units(unittype).closer_than(8, self.home_ramp_location)
                    for unit in far_from_ramp:
                        if unit.is_idle:
                            await self.api.do(unit.move(self.home_ramp_location))
                end = time.time()
                print("Move to defence: {}".format(end - start))

        # for unit in units_for_defence:
        #    if unit.is_idle:
        #        self.api.do(unit.move(self.home_ramp))

    def units_under_attack(self):
        units = []
        # Check if the health has changed
        for unit in self.api.units:
            prev_health = self.unit_healths.get(unit.tag, None)
            if prev_health is None:
                self.unit_healths[unit.tag] = unit.health
            else:
                # Health has decresed and unit is alive
                if self.unit_healths[unit.tag] > unit.health and unit.health > 0:
                    units.append(unit.tag)
        return units

    async def harass(self, iteration):

        # Check build
        if build_turn(iteration, 1) and self.api.units(STARGATE).exists:
            # Build initial Oracles
            if self.oracle_count < ORACLE_HARASS:
                for stargate in self.api.units(STARGATE).ready.noqueue:
                    if self.api.can_afford(ORACLE):
                        await self.api.do(stargate.train(ORACLE))
                        self.oracle_count += 1

        if iteration % 100 == 0:
            for oracle in self.api.units(ORACLE):
                await self.attack_to_best_enemy_with(oracle)

    async def build_num_of(self, number_of_units, unit_type, iteration):
        if build_turn(iteration, 2):
            # Not our time
            return

        if unit_type not in UNIT_BUILDER_MAP:
            raise Exception('unit type {} not defined!' .format(unit_type))
            pass

        if len(self.api.units(unit_type)) < number_of_units:
            for building_unit in self.api.units(UNIT_BUILDER_MAP[unit_type]).ready.noqueue:
                if self.api.can_afford(unit_type):
                    print("Building unit {}".format(unit_type))
                    await self.api.do(building_unit.train(unit_type))

    async def build_shitload_of_units(self, iteration):
        for unit_type, num_units in NUM_UNIT_BUILDS.items():
            await self.build_num_of(num_units, unit_type, iteration)

    async def attack_with_all_we_got(self):
        all_attacking_units = self.get_all_attacking_units()

        if len(all_attacking_units) < sum(NUM_UNIT_BUILDS.values()) / 2:
            return

        valid_attackers = [
            unit for unit in all_attacking_units if unit.is_idle]
        if len(valid_attackers) == 0:
            return

        print("Attacking with {} units".format(len(valid_attackers)))
        for attacker in valid_attackers:
            await self.attack_to_best_enemy_with(attacker)

    async def attack_to_best_enemy_with(self, attacker):
        await self.api.do(attacker.attack(self.best_enemy_position()))

    def best_enemy_position(self):
        possible_places = [
            self.api.known_enemy_units,
            self.api.known_enemy_structures,
            self.api.enemy_start_locations
        ]

        for target in possible_places:
            if len(target) > 0:
                return target[0]

    def get_all_attacking_units(self):
        units = []
        for unit_type in UNIT_BUILDER_MAP:
            for unit in self.api.units(unit_type):
                units.append(unit)
        return units

    def get_all_units_by_types(self, unittypes):
        units = []
        for unittype in unittypes:
            units.extend(self.api.units(unittype))
        return units

    def get_all_units_by_type(self, unittype):
        return self.api.units(unittype)


UNIT_BUILDER_MAP = {
    ZEALOT: GATEWAY,
    STALKER: GATEWAY,
    ADEPT: GATEWAY,
    SENTRY: GATEWAY,
    MOTHERSHIPCORE: GATEWAY
}

NUM_UNIT_BUILDS = {
    ADEPT: 5,
    STALKER: 10,
    SENTRY: 5,
    ZEALOT: 3,
    MOTHERSHIPCORE: 1
}
