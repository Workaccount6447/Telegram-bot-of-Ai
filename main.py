from telegram import Update
from telegram.ext import Application, ChatJoinRequestHandler, ContextTypes
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Auto-approve handler
async def auto_approve_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.chat_join_request.approve()
    print(f"✅ Approved: {update.chat_join_request.from_user.full_name} in {update.chat_join_request.chat.title}")

# Non-async main for Koyeb compatibility
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(ChatJoinRequestHandler(auto_approve_all))
    print("🤖 Bot is running and auto-approving all join requests...")
    app.run_polling()

if __name__ == "__main__":
    main()
