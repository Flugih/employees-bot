from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

from infrastructure import Config, CreateBot
from service import Handlers, DBManager
from domain import EmployeeService


class SchedulerService:
    def __init__(self, client):
        from core import UserChecker # temp

        self.config = Config()
        self.handler = Handlers()
        self.scheduler = AsyncIOScheduler()
        self.database = DBManager()
        self.employee_service = EmployeeService()
        self.client = client
        self.user_checker = UserChecker(self.client)

    def start(self):
        logging.info("Starting scheduler...")
        self.scheduler.add_job(self.check_users, 'cron', hour=self.config.CHECK_TIME, minute=0)
        self.scheduler.start()

    async def check_users(self):
        logging.info("Checking users in chats...")
        await self.user_checker.compare_all_chats()
