import json
from pathlib import Path

import sc2
from .war import War
from .build import Build


class MyBot(sc2.BotAI):
    with open(Path(__file__).parent / "../botinfo.json") as f:
        NAME = json.load(f)["name"]

    def __init__(self):
        self.war = War(self)
        self.build = Build(self)

    async def on_step(self, iteration):
        await self.war.on_step(iteration)
        await self.build.on_step(iteration)
