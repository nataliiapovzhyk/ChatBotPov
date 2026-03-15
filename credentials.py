import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")
    ChatGPT_TOKEN: str = os.getenv("CHAT_GPT_TOKEN")

    admin_password = os.getenv("ADMIN_PASSWORD")

config = Config()
config.BOT_TOKEN
config.ChatGPT_TOKEN
