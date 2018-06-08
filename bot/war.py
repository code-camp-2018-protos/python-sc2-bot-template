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
        self.home_ramp = None
        self.unit_healths = {} # Tag, Health

    async def on_step(self, iteration):
        # await self.attack_with_first_worker()
        await self.build_shitload_of_zealots(iteration)
        await self.attack_with_all_we_got()
        await self.move_to_defensive()
        await self.harass(iteration)
        
    async def on_start(self):
        ## TODO Get home ramp location
        pass

    async def move_to_defensive(self):
        """Move unit to stand between own and enemy.
        Priotise saving units over watching the ramp.
        """
        units_for_defence = self.get_all_units_by_types([ZEALOT, ADEPT, STALKER])
        #print(self.api.game_info.map_ramps.closest_to(self.api.units(NEXUS).first))
        
        units_under_attack = self.units_under_attack()
        if units_under_attack: # Check if empty
            for unit in units_for_defence:
                if unit.is_idle:
                    self.api.do(unit.move(self.api.units.by_tag(units_under_attack[0]).location))    
        

        #for unit in units_for_defence:
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
                if self.unit_healths[unit.tag] > unit.health:
                    units.append(unit.tag)
        return units

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

        await self.build_shitload_of_stalkers(iteration)
        await self.build_shitload_of_adepts(iteration)
        await self.attack_with_all_we_got()

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

    async def build_shitload_of_zealots(self, iteration):
        await self.build_num_of(3, ZEALOT, iteration)

    async def build_shitload_of_stalkers(self, iteration):
        await self.build_num_of(3, STALKER, iteration)

    async def build_shitload_of_adepts(self, iteration):
        await self.build_num_of(5, ADEPT, iteration)

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

    def get_all_units_by_types(self, unittypes):
        units = []
        for unit_type in unittypes:
            units.extend(self.api.units(unit_type))
        return units


UNIT_BUILDER_MAP = {
    ZEALOT: GATEWAY,
    STALKER: GATEWAY,
    ADEPT: GATEWAY
}
