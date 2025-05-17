from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp

@dp.message_handler(Command("start"))
async def start_command(message: types.Message):
    user_first_name = message.from_user.first_name
    start_text = (
        f"🎉 *Welcome {user_first_name}!* 🎉\n\n"
        "✨ *I'm your personal AI assistant* ✨\n\n"
        "🤖 How can I assist you today?\n\n"
        "🔥 *Features*:\n"
        "✅ 100% Free & Unlimited\n"
        "✅ Instant Responses\n"
        "✅ Memory Across Chats\n"
        "✅ Image Generator\n\n"
        "📝 *Quick Commands*:\n\n"
        "/start – Begin interacting with the bot, new chat.\n"
        "/img <prompt> – Generate an image using AI.\n"
        "/summarise <YouTube_Link> – Get a summary of a YouTube video via AI.\n"
        "/privacypolicy – View our data handling and privacy policy.\n"
        "/help – Show help message.\n\n"
        "⚡ *Features*\n"
        "• Unlimited\n"
        "• 3x Faster Responses\n"
        "• 32K Context Memory\n\n"
        "⚒ Support: @Smartautomationsuppport_bot\n\n"
        "🚀 Powered by: @smartautomations"
    )
    await message.reply(start_text, parse_mode="Markdown")