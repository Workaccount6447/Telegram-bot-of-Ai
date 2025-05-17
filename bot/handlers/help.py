from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp

@dp.message_handler(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "🆘 *@smartautomations_bot Help* 🆘\n"
        "────────────────────\n"
        "💬 *How to chat*:\n"
        "Just type messages like:\n"
        "• \"Explain quantum physics ⚛️\"\n"
        "• \"Write a haiku about cats 🐱\"\n\n"
        "⚙️ *Commands*:\n\n"
        "/start – Begin interacting with the bot, new chat.\n"
        "/img <prompt> – Generate an image using AI.\n"
        "/summarise <YouTube_Link> – Get a summary of a YouTube video via AI.\n"
        "/privacypolicy – View our data handling and privacy policy.\n"
        "/help – Show this help message.\n\n"
        "📏 *Limits*:\n"
        "4000 chars/message (we auto-split 📜)\n\n"
        "🔋 *Status*: Operational ✅"
    )
    await message.reply(help_text, parse_mode="Markdown")