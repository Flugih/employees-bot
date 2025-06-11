import logging

from infrastructure import CreateBot
from service import DBManager, Handlers
from domain import EmployeeService


class UserChecker:
    def __init__(self, client):
        self.handler = Handlers()
        self.client = client
        self.database = DBManager()
        self.employee = EmployeeService()

    async def get_lists(self, chat_id):
        tg_list = await self.handler.get_chat_member(self.client, int(chat_id))
        service_list = await self.employee.get_employees()

        return tg_list, service_list

    async def compare_lists(self, tg_list, service_list, chat_id):
        mismatched_users = []
        whitelist = await self.database.get_whitelist(chat_id)

        for username, user_id in tg_list:
            if not any(username in service_name for service_name in service_list) and not any(username in whitelist_name for whitelist_name in whitelist):
                mismatched_users.append((username, user_id))

        return mismatched_users

    async def compare_all_chats(self):
        chat_ids = await self.database.get_all_chat_ids()

        for chat_id in chat_ids:
            status = await self.database.get_status(chat_id)

            if status:
                tg_list, service_list = await self.get_lists(int(chat_id))
                mismatched_users = await self.compare_lists(tg_list, service_list, chat_id)

                if mismatched_users:
                    await self.handler.display_user_list_to_kick(self.client, int(chat_id), mismatched_users)
