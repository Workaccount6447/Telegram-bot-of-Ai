from aiogram import Bot, Dispatcher, executor, types
import logging
import asyncio
import os

# Load token from environment or config file
API_TOKEN = os.getenv('BOT_TOKEN', 'your-default-token-here')

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def register_handlers():
    import logging
    logging.basicConfig(level=logging.INFO)
    from api import app
    from aiogram import types, Dispatcher, Bot

    import bot.handlers
    from bot import WEBHOOK_PATH, dp, client

    @app.post(WEBHOOK_PATH)
    async def bot_webhooks_endpoint(update: dict):
        telegram_update = types.Update(**update)
        Dispatcher.set_current(dp)
        Bot.set_current(client)
        await dp.process_update(telegram_update)

def start_bot():
    register_handlers()
    executor.start_polling(dp, skip_updates=True)

if __name__ == '__main__':
    start_bot()