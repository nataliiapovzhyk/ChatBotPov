import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    token = os.getenv("BOT_TOKEN")
    admin_password = os.getenv("ADMIN_PASSWORD")

config = Config()
config.token
