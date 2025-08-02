from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import json
import os

# === CONFIG ===
BOT_TOKEN = "8009237833:AAFn0FntFqrX9dna1R0Dv9UZakO-aMRRatE"  # Replace this
OWNER_ID = 7588665244          # Replace with your Telegram user ID
DATA_FILE = "userdata.json"

# === DATA SETUP ===
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# === COMMANDS ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if user_id not in data:
        await update.message.reply_text(
            "TO USE THIS BOT KINDLY PAY WHOLE CONSULTING WITH OUR TEAM.\n"
            "OUR SUPPORT BOT - @amazonsupportrobot"
        )
        return

    keyboard = [
        [InlineKeyboardButton("📦 Amazon Tag", callback_data="set_tag")],
        [InlineKeyboardButton("📣 Channel", callback_data="set_channel")]
    ]
    await update.message.reply_text("SETUP PANEL", reply_markup=InlineKeyboardMarkup(keyboard))

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ You are not authorized.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /adduser <user_id>")
        return

    user_id = context.args[0].lstrip("@")
    data = load_data()
    if user_id not in data:
        data[user_id] = {}
        save_data(data)

    await update.message.reply_text("✅ User added successfully.")

    try:
        await context.bot.send_message(
            chat_id=int(user_id),
            text="YOU ARE NOW ALLOWED TO USE THIS BOT, KINDLY SEND /START AGAIN TO USE THIS BOT PROPERLY"
        )
    except:
        await update.message.reply_text("⚠️ Couldn't message the user.")

# === CALLBACK BUTTON ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)

    if query.data == "set_tag":
        context.user_data["awaiting_tag"] = True
        await query.message.reply_text("Please send your Amazon tag (e.g., dealsduniya-21).")

    elif query.data == "set_channel":
        await query.message.reply_text(
            "Add me to your channel, make me admin, then forward any message from that channel here."
        )
        context.user_data["awaiting_channel"] = True

# === TEXT HANDLER ===
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()

    if context.user_data.get("awaiting_tag"):
        data[user_id]["tag"] = update.message.text.strip()
        save_data(data)
        context.user_data["awaiting_tag"] = False
        await update.message.reply_text("✅ Tag saved.")
        return

    if context.user_data.get("awaiting_channel") and update.message.forward_from_chat:
        chat = update.message.forward_from_chat
        bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)

        if bot_member.status in ['administrator', 'creator']:
            data[user_id]["channel"] = chat.id
            save_data(data)
            context.user_data["awaiting_channel"] = False
            await update.message.reply_text("✅ Your Channel Successfully Setupped.")
        else:
            await update.message.reply_text("❌ Try Again. Bot is not admin in the channel.")

# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, message_handler))

    print("🤖 Bot started.")
    app.run_polling()

if __name__ == "__main__":
    main()
