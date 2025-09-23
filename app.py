# om ganesha namah
# Jai shree krishna 
import logging
import re
import asyncio
import socket
from telegram import Update, MessageThreadId
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==========================
# CONFIG
# ==========================
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
GROUP_ID = -1002906782286
OWNER_ID = 7588665244

# ==========================
# LOGGING
# ==========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==========================
# HEALTH CHECK DUMMY SERVER
# ==========================
async def start_health_server():
    async def handle_client(reader, writer):
        writer.write(b"OK\n")
        await writer.drain()
        writer.close()

    server = await asyncio.start_server(handle_client, "0.0.0.0", 8080)
    logger.info("Health check server running on port 8080")
    async with server:
        await server.serve_forever()

# ==========================
# HELPERS
# ==========================
def extract_url(text: str):
    url_pattern = r"(https?://[^\s]+)"
    match = re.search(url_pattern, text)
    return match.group(0) if match else None

async def fetch_photo_from_url(url: str):
    # Placeholder function – here you integrate your real fetcher
    return "https://via.placeholder.com/500x300.png?text=Fetched+Image"

# ==========================
# HANDLERS
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("✅ Bot is running!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    url = extract_url(update.message.text)
    if not url:
        return

    user = update.effective_user

    # Notify user privately
    try:
        await context.bot.send_message(chat_id=user.id, text="⏳ Fetching photo...")
    except Exception as e:
        logger.warning(f"Could not send private message to {user.id}: {e}")

    # Simulate fetch
    photo_url = await fetch_photo_from_url(url)

    # Reply in thread under user’s message
    try:
        await update.message.reply_photo(
            photo=photo_url,
            caption=f"📸 Here is the preview for:\n{url}",
            message_thread_id=update.message.message_thread_id if update.message.is_topic_message else None
        )
    except Exception as e:
        logger.error(f"Failed to send photo: {e}")

# ==========================
# MAIN
# ==========================
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Run both bot and health server
    await asyncio.gather(
        app.run_polling(poll_interval=30),
        start_health_server()
    )

if __name__ == "__main__":
    asyncio.run(main())
