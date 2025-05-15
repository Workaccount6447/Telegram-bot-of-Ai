import logging
logging.basicConfig(level=logging.INFO)
import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    SERVERLESS = True
    WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")
    PORT = int(os.getenv("PORT", 8080))
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")