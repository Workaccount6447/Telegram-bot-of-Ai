import os
# ===== File: start.py =====
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from model_selector import user_current_model

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_current_model[user.id] = None

    keyboard = [
        [InlineKeyboardButton("Model", callback_data="model_menu")],
        [InlineKeyboardButton("Mode", callback_data="mode_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = f"""🎉 Welcome {user.first_name}! 🎉

✨ I'm your personal AI assistant ✨

🤖 How can I assist you today?

🔥 Features: ✅ 100% Free & Unlimited ✅ Instant Responses ✅ Memory Across Chats

📝 Quick Commands:
/start – Begin interacting with the bot, new chat.
/summarise – Get a summary of a YouTube video via AI.
/privacypolicy – View our data handling and privacy policy.
/help – Show help message.

⚡ Features • Unlimited • 3x Faster Responses • 32K Context Memory

⚒ Support: @Smartautomationsuppport_bot

🚀 Powered by: @smartautomations
"""
    await update.message.reply_text(message, reply_markup=reply_markup)

# ===== File: model_selector.py =====
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

user_current_model = {}

async def model_selector_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "model_menu":
        keyboard = [
            [InlineKeyboardButton("Gemini 2.5 Flash", callback_data="model_gemini")],
            [InlineKeyboardButton("ChatGPT", callback_data="model_llama")],
        ]
        await query.edit_message_text("Select a model:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    model_map = {
        "model_gemini": "google/gemini-pro-2.5-flash",
        "model_llama": "meta-llama/llama-3-70b-instruct",
    }
    selected_model = model_map.get(query.data)
    if selected_model:
        user_current_model[query.from_user.id] = selected_model
        label = query.data.replace("model_", "").capitalize()
        await query.edit_message_text(f"You selected “{label}” for Chatting.\nIf you have or face any problem, contact us on @Smartautomationsuppport_bot")

# ===== File: mode_selector.py =====
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from model_selector import user_current_model

async def mode_selector_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "mode_menu":
        keyboard = [
            [InlineKeyboardButton("🧠 Deep Reasoning", callback_data="mode_qwen_reasoning")],
            [InlineKeyboardButton("💬 Dialogue and Chat", callback_data="mode_llama_chat")],
            [InlineKeyboardButton("🧑‍💻 Coding", callback_data="mode_qwen_coder")],
            [InlineKeyboardButton("📊 Business and Analysis", callback_data="mode_llama_biz")],
        ]
        await query.edit_message_text("Select a mode:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    mode_map = {
        "mode_qwen_reasoning": "qwen/qwen-2-72b-instruct",
        "mode_llama_chat": "meta-llama/llama-3-70b-instruct",
        "mode_qwen_coder": "openrouter/quen-2.5-coder-32b",
        "mode_llama_biz": "meta-llama/llama-3-70b-instruct",
    }
    selected_model = mode_map.get(query.data)
    if selected_model:
        user_current_model[query.from_user.id] = selected_model
        label = query.data.split("_", 1)[1].replace("_", " ").title()
        await query.edit_message_text(f"You selected “{label}” for Chatting.\nIf you have or face any problem, contact us on @Smartautomationsuppport_bot")

# ===== File: chat_handler.py =====
import requests
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from model_selector import user_current_model

OPENROUTER_API_KEY = "your_openrouter_api_key_here"

def call_openrouter(model_id, user_message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model_id,
        "messages": [{"role": "user", "content": user_message}],
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

async def chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    model_id = user_current_model.get(user_id)
    if not model_id:
        await update.message.reply_text("Please select a model or mode first.")
        return

    user_message = update.message.text
    try:
        reply = call_openrouter(model_id, user_message)
        if "coder" in model_id.lower():
            reply = f"```python\n{reply}\n```"
            await update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("An error occurred while processing your request.")

# ===== File: summarise.py =====
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

async def summarise_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        await update.message.reply_text("Please provide a YouTube link.\nExample: /summarise https://youtube.com/watch?v=XXXX")
        return

    url = args[0]
    await update.message.reply_text(f"Summarizing video from: {url}\n(This is a placeholder)")

# ===== File: main.py =====
import logging
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from start import start
from summarise import summarise_command
from model_selector import model_selector_handler
from mode_selector import mode_selector_handler
from chat_handler import chat_handler

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

logging.basicConfig(level=logging.INFO)
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("summarise", summarise_command))
app.add_handler(CallbackQueryHandler(model_selector_handler, pattern="^model_"))
app.add_handler(CallbackQueryHandler(mode_selector_handler, pattern="^mode_"))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat_handler))

app.run_polling()

@bot.message_handler(commands=["announce"])
def announce_command(message):
    if message.from_user.id != 7588665244:
        bot.reply_to(message, "You are not authorized to use this command.")
        return

    msg = bot.reply_to(message, "Please send the announcement text:")
    bot.register_next_step_handler(msg, process_announcement)

def process_announcement(message):
    announcement_text = message.text
    count = 0
    failed = 0

    # Load user IDs from database or file
    try:
        with open("users.txt", "r") as f:
            user_ids = [int(line.strip()) for line in f if line.strip().isdigit()]
    except FileNotFoundError:
        bot.reply_to(message, "No users found.")
        return

    for user_id in user_ids:
        try:
            bot.send_message(user_id, f"**Announcement:**\n{announcement_text}", parse_mode="Markdown")
            count += 1
        except Exception:
            failed += 1

    bot.reply_to(message, f"Announcement sent to {count} users. Failed to send to {failed} users.")


