import asyncio
import logging
from pyrogram import filters, idle
from pyrogram.handlers import MessageHandler, ChatMemberUpdatedHandler

from service import Handlers, DBManager, Fix
from core import SchedulerService
from infrastructure import CreateBot, LoggerManager


class Bot:
    def __init__(self):
        from core import UserChecker

        Fix()
        self.logger = LoggerManager()
        self.logger.setup_logging()
        self.handler = Handlers()
        self.client = CreateBot().get_client()
        self.scheduler = SchedulerService(self.client)
        self.database = DBManager()
        self.pyrogram_logger = logging.getLogger("pyrogram")

        self.user_checker = UserChecker(self.client)

    def register_handlers(self):
        self.client.add_handler(ChatMemberUpdatedHandler(self.handler.on_chat_member_updated))

        self.client.add_handler(MessageHandler(self.handler.private_commands_start, filters.private & filters.command("start")))
        self.client.add_handler(MessageHandler(self.handler.commands_info, filters.command("info")))

        self.client.add_handler(MessageHandler(self.handler.activate_bot_in_chat, filters.command("activate")))
        self.client.add_handler(MessageHandler(self.handler.deactivate_bot_in_chat, filters.command("deactivate")))

        self.client.add_handler(MessageHandler(self.handler.whitelist_add, filters.command("whitelist_add")))
        self.client.add_handler(MessageHandler(self.handler.whitelist_remove, filters.command("whitelist_remove")))
        self.client.add_handler(MessageHandler(self.handler.whitelist_show, filters.command("whitelist_show")))
        self.client.add_handler(MessageHandler(self.handler.approve_kick, filters.command("approve_kick")))

    async def start(self):
        await self.database.create_table()
        self.pyrogram_logger.info('Bot is started!')
        await self.client.start()
        self.register_handlers()

        await self.user_checker.compare_all_chats()

        # self.scheduler.start()
        await idle()


if __name__ == "__main__":
    bot = Bot()

    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(bot.start())
    else:
        loop.run_until_complete(bot.start())