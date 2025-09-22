import logging
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    Application, CommandHandler,
    MessageHandler, filters,
    ContextTypes
)

# ---------------- CONFIG ----------------
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"  # Hardcoded token
OWNER_ID = 7588665244
DATABASE_GROUP_ID = -1002906782286  # group used as database

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- HEALTH CHECK SERVER ----------------
def run_web():
    """Run a dummy HTTP server for Koyeb health checks."""
    port = int(os.environ.get("PORT", 7860))  # Koyeb sets PORT automatically
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    logging.info(f"✅ Health check server running on port {port}")
    server.serve_forever()

threading.Thread(target=run_web, daemon=True).start()

# ---------------- HELPERS ----------------
def now_ist():
    """Return current IST datetime."""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

async def send_to_database(context: ContextTypes.DEFAULT_TYPE, text: str):
    """Send text to database group (acts like logging)."""
    await context.bot.send_message(chat_id=DATABASE_GROUP_ID, text=text)

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! 👋 Bot is alive on Koyeb 🚀")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start polling
    app.run_polling()

if __name__ == "__main__":
    main()
