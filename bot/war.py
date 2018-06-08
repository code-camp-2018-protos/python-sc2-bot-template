class War():
    def __init__(self, api):
        self.api = api

    async def on_step(self, iteration):
        await self.chat_send("ATTACK!!!")
