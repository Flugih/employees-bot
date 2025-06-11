from pyrogram import Client


class CreateBot:
    def __init__(self):
        from infrastructure import Config # temp

        self.bot_config = Config()
        self.client = Client("my_bot",api_id=self.bot_config.API_ID,api_hash=self.bot_config.API_HASH,bot_token=self.bot_config.BOT_TOKEN)

    async def start(self):
        await self.client.start()

    def get_client(self) -> Client:
        return self.client
