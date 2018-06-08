import json
from pathlib import Path

import sc2
from .war import War
from .build import Build
from .upgrader import Upgrader


class MyBot(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self.war = War(self)
        self.builder = Build(self)
        self.upgrader = Upgrader(self)

    async def on_step(self, iteration):
        await self.war.on_step(iteration)
        await self.builder.on_step(iteration)
        await self.upgrader.on_step(iteration)
