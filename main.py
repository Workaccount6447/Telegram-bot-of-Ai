from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Automatically approve all join requests
async def auto_approve_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.chat_join_request.approve()
    print(f"✅ Approved: {update.chat_join_request.from_user.full_name} in {update.chat_join_request.chat.title}")

# Main function
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve_all))
    print("🤖 Bot is running and auto-approving all join requests...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
