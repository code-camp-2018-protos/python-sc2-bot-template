class Build():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        await self.api.chat_send("BUILD!!!")
