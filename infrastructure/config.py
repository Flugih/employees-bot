import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.LOG_LEVEL_ROOT = os.getenv("LOG_LEVEL_ROOT", "DEBUG")
        self.LOG_LEVEL_USER_ACTIONS = os.getenv("LOG_LEVEL_USER_ACTIONS", "DEBUG")
        self.LOG_LEVEL_PYROGRAM = os.getenv("LOG_LEVEL_PYROGRAM", "INFO")
        self.API_ID = int(os.getenv("API_ID", "your_api_id"))
        self.API_HASH = os.getenv("API_HASH", "your_api_hash")
        self.BOT_TOKEN = os.getenv("BOT_TOKEN", "your_bot_token")
        self.SESSION_NAME = os.getenv("SESSION_NAME", "userbot_session")
        self.EMPLOYEE_SERVICE_URL = os.getenv("EMPLOYEE_SERVICE_URL", "url")
        self.CHECK_TIME = int(os.getenv("CHECK_TIME", 12))  # Интервал проверки в минутах
        self.DB_URL = os.getenv("DB_URL", "sqlite://database.db")
