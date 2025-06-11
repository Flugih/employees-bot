import logging

from pyrogram.enums import ChatMemberStatus


class Handlers:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Handlers, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        from service import DBManager

        self.pending_kick_list = {}
        self.database = DBManager()

        self.user_actions_logger = logging.getLogger('user_actions')
        self.pyrogram_logger = logging.getLogger('pyrogram')

    async def is_bot_admin_and_group_is_supergroup(self, client, chat_id: int) -> bool:
        try:
            if not str(chat_id).startswith("-100"):
                self.user_actions_logger.warning(f"Chat {chat_id} is not a supergroup")
                return False

            bot_member = await client.get_chat_member(chat_id, client.me.id)
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                self.user_actions_logger.warning(f"Bot is not an administrator in chat {chat_id}. Status: {bot_member.status}")
                return False

            return True

        except Exception as e:
            self.pyrogram_logger.error(f"Error checking bot admin status or supergroup status for chat {chat_id}: {e}")
            return False

    async def on_chat_member_updated(self, client, update):
        if update.new_chat_member and update.new_chat_member.user:
            if update.new_chat_member.user.is_bot and update.new_chat_member.user.id == client.me.id:
                chat_id = update.chat.id

                try:
                    self.user_actions_logger.info(f"Bot added to chat {chat_id}.")
                    await client.send_message(chat_id=update.chat.id, text="/info чтобы получить информацию о боте. Default chat status is 'True'")

                    if await self.is_bot_admin_and_group_is_supergroup(client, chat_id):
                        await self.database.update_status(chat_id, True)
                        return

                except ValueError as e:
                    self.pyrogram_logger.error(f"Error message not sent to chat {chat_id}: {e}")

        if update.chat and update.old_chat_member:
            if update.old_chat_member.user.is_bot and update.old_chat_member.user.id == client.me.id:
                chat_id = update.chat.id

                self.user_actions_logger.info(f"Bot was removed from chat: {chat_id}")
                await self.database.update_status(chat_id, False)

    async def private_commands_start(self, client, message):
        self.user_actions_logger.info(f"Received /start command from {message.from_user.username}")
        await message.reply_text("Привет! Я бот, который следит за списком сотрудников")

    async def commands_info(self, client, message):
        self.user_actions_logger.info(f"Received /info command from {message.from_user.username}")
        await message.reply_text("Доступные команды в чат:\n/activate - включить бота\n/deactivate - выключить бота\n/whitelist_show - показать список вайт-листа\n/whitelist_add [username] - добавить в вайт-лист\n/whitelist_remove [username] - удалить из вайт-листа")

    async def activate_bot_in_chat(self, client, message):
        chat_id = message.chat.id

        is_valid_group = await self.is_bot_admin_and_group_is_supergroup(client, chat_id)
        if not is_valid_group:
            self.user_actions_logger.warning(f"Failed to activate bot in chat {chat_id}: not a supergroup or bot is not admin")
            return await message.reply_text("Для активации бота группа должна быть супергруппой и бот должен быть администратором.")

        await self.database.ensure_chat_exists(chat_id, True)

        current_status = await self.database.get_status(chat_id)

        if current_status:
            self.user_actions_logger.info(f"Bot is already activated in chat {chat_id}")
            await message.reply_text(f"{message.chat.id} Бот уже активирован в этом чате")
        else:
            self.user_actions_logger.info(f"Bot is activated on chat: {chat_id}")
            await self.database.update_status(chat_id, True)

            await message.reply_text("Бот активирован в этом чате. Теперь вы можете использовать все его функции")

    async def deactivate_bot_in_chat(self, client, message):
        chat_id = message.chat.id

        is_valid_group = await self.is_bot_admin_and_group_is_supergroup(client, chat_id)
        if not is_valid_group:
            self.user_actions_logger.warning(f"Failed to deactivate bot in chat {chat_id}: not a supergroup or bot is not admin")
            return await message.reply_text("Для деактивации бота группа должна быть супергруппой и бот должен быть администратором.")

        await self.database.ensure_chat_exists(chat_id, False)

        current_status = await self.database.get_status(chat_id)

        if not current_status:
            self.user_actions_logger.info(f"Bot is already deactivated in chat {chat_id}")
            await message.reply_text("Бот уже деактивирован в этом чате")
        else:
            self.user_actions_logger.info(f"Bot is deactivated on chat: {chat_id}")
            await self.database.update_status(chat_id, False)

            await message.reply_text("Бот деактивирован в этом чате. Если вам понадобятся его функции, вы можете активировать его снова")

    async def kick_user_from_chat(self, client, chat_id: int, user_tag: str):
        try:
            await client.kick_chat_member(chat_id, user_tag)
            self.user_actions_logger.info(f"User {user_tag} kicked from chat {chat_id}.")

        except Exception as e:
            self.pyrogram_logger.error(f"Failed to kick user {user_tag} from chat {chat_id}: {e}")

    async def get_chat_member(self, client, chat_id: int) -> list:
        members = []

        async for member in client.get_chat_members(chat_id):
            username = member.user.username if member.user.username else "No username"
            members.append((username, member.user.id))

        self.user_actions_logger.info(f"Retrieved {len(members)} members for chat {chat_id}")
        return members

    async def display_user_list_to_kick(self, client, chat_id: int, user_list: list):
        formatted_list = "\n".join([f"{user_tag} (ID: {user_id})" for user_tag, user_id in user_list])
        message = f"Список пользователей для удаления:\n{formatted_list}\n\nДля подтверждения введите /approve_kick"

        self.pending_kick_list[int(chat_id)] = user_list

        self.user_actions_logger.info(f"Displaying kick list for chat {chat_id}: {len(user_list)} users to be kicked.")

        await client.send_message(chat_id, message)

    async def approve_kick(self, client, message):
        chat_id = message.chat.id
        to_kick = self.pending_kick_list.get(int(chat_id), [])  # список айдишников данного чата

        if not to_kick:
            self.user_actions_logger.info(f"No users to kick in chat {chat_id}")
            return await message.reply_text("Нет пользователей на удаление.")

        del self.pending_kick_list[chat_id]

        for user_tag, user_id in to_kick:
            try:
                await client.ban_chat_member(chat_id, user_id)
                await client.unban_chat_member(chat_id, user_id)
                self.user_actions_logger.info(f"Kicked user {user_tag} (ID: {user_id}) from chat {chat_id}.")
                await message.reply_text(f"Пользователь {user_tag} был удален.")
            except Exception as e:
                self.pyrogram_logger.error(f"Ошибка при удалении {user_tag} (ID: {user_id}) из чата {chat_id}: {e}")

    async def whitelist_add(self, client, message):
        chat_id = message.chat.id

        is_valid_group = await self.is_bot_admin_and_group_is_supergroup(client, chat_id)
        if not is_valid_group:
            self.user_actions_logger.warning(f"Failed to add to whitelist in chat {chat_id}: not a supergroup or bot is not admin")
            return await message.reply_text("Для добавления в вайт-лист группа должна быть супергруппой и бот должен быть администратором.")

        current_status = await self.database.get_status(chat_id)

        if not current_status:
            self.user_actions_logger.warning(f"Bot is not activated in chat {chat_id}")
            return await message.reply_text("Бот не активирован в этом чате. Используйте команду /activate для активации")

        if len(message.command) < 2:
            self.user_actions_logger.warning(f"No username provided for whitelist addition in chat {chat_id}")
            return await message.reply_text("Укажите юзернейм: /whitelist_add @username")

        try:
            user_tag = message.command[1]  # получаем юзернейм
            await self.database.add_to_whitelist(chat_id, user_tag)
            self.user_actions_logger.info(f"User {user_tag} added to whitelist in chat {chat_id}")
            await message.reply_text(f"Пользователь {user_tag} добавлен в вайт-лист чата.")

        except Exception as e:
            self.pyrogram_logger.error(f"Error adding {user_tag} to whitelist in chat {chat_id}: {e}")
            await message.reply_text(f"Произошла ошибка при добавлении пользователя в вайт-лист: {e}")

    async def whitelist_remove(self, client, message):
        chat_id = message.chat.id

        is_valid_group = await self.is_bot_admin_and_group_is_supergroup(client, chat_id)
        if not is_valid_group:
            self.user_actions_logger.warning(f"Failed to remove from whitelist in chat {chat_id}: not a supergroup or bot is not admin")
            return await message.reply_text("Для удаления из вайт-листа группа должна быть супергруппой и бот должен быть администратором.")

        current_status = await self.database.get_status(chat_id)

        if not current_status:
            self.user_actions_logger.warning(f"Bot is not activated in chat {chat_id}")
            return await message.reply_text("Бот не активирован в этом чате. Используйте команду /activate для активации")

        if len(message.command) < 2:
            self.user_actions_logger.warning(f"No username provided for whitelist removal in chat {chat_id}")
            return await message.reply_text("Укажите юзернейм: /whitelist_remove @username")

        try:
            user_tag = message.command[1]  # получает 1 аргумент
            await self.database.remove_from_whitelist(chat_id, user_tag)
            self.user_actions_logger.info(f"User {user_tag} removed from whitelist in chat {chat_id}")
            await message.reply_text(f"Пользователь {user_tag} удален из вайт-листа чата.")

        except Exception as e:
            self.pyrogram_logger.error(f"Error removing {user_tag} from whitelist in chat {chat_id}: {e}")
            await message.reply_text(f"Произошла ошибка при удалении пользователя из вайт-листа: {e}")

    async def whitelist_show(self, client, message):
        chat_id = message.chat.id
        current_status = await self.database.get_status(chat_id)
        whitelist = await self.database.get_whitelist(chat_id)

        if not current_status:
            self.user_actions_logger.warning(f"Bot is not activated in chat {chat_id}")
            return await message.reply_text("Бот не активирован в этом чате. Используйте команду /activate для активации")

        if not isinstance(whitelist, list):
            whitelist = []

        if not whitelist:
            self.user_actions_logger.info(f"Whitelist is empty in chat {chat_id}")
            return await message.reply_text("Вайт-лист пуст.")

        user_list = "\n".join([f"- {user_tag}" for user_tag in whitelist])

        self.user_actions_logger.info(f"Displaying whitelist for chat {chat_id}: {len(whitelist)} users in the list")

        await message.reply_text(f"Вайт-лист чата:\n{user_list}")