# om ganesha namah
# Jai shree krishna 
import logging
import requests
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ---------------------------
# Config
# ---------------------------
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
GROUP_ID = -1002906782286
OWNER_ID = 7588665244

# ---------------------------
# Logger
# ---------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------------------------
# Dummy server for health check
# ---------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running", 200

# ---------------------------
# Handlers
# ---------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me any link and I will capture its screenshot 📸")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    link = update.message.text.strip()

    if not link.startswith("http"):
        await update.message.reply_text("❌ Please send a valid link starting with http or https.")
        return

    # Tell user fetching started
    await update.message.reply_text("⏳ Fetching screenshot, please wait...")

    try:
        # Take screenshot (via thum.io free API demo)
        screenshot_url = f"https://image.thum.io/get/width/1200/{link}"

        # Send screenshot back
        await update.message.reply_photo(photo=screenshot_url, caption="✅ Here is your screenshot")

        # Log in group (threaded by user)
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"📸 Screenshot fetched for user [{user.first_name}](tg://user?id={user.id})\n🔗 {link}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("⚠️ Failed to capture screenshot. Try another link.")

# ---------------------------
# Main
# ---------------------------
def main():
    # Start telegram bot
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # Run polling with 30s timeout
    application.run_polling(poll_interval=30)

if __name__ == "__main__":
    import threading

    # Run dummy Flask server for TCP health checks
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=8080), daemon=True).start()

    main()
