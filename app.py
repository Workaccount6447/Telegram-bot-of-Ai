import logging
import requests
import urllib.parse
import os
import threading
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    Application, CommandHandler,
    MessageHandler, filters,
    ContextTypes )
from http.server import SimpleHTTPRequestHandler, HTTPServer




# ---------------- CONFIG ----------------
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
OWNER_ID = 7588665244
DATABASE_GROUP_ID = -1002906782286  # group used as database

# ---------------- LOGGING ----------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------------- HELPERS ----------------
def now_ist():
    """Return current IST datetime."""
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

async def send_to_database(context: ContextTypes.DEFAULT_TYPE, text: str):
    """Send info to database group."""
    await context.bot.send_message(DATABASE_GROUP_ID, text)

def run_web():
    """Run a dummy HTTP server for Koyeb health checks."""
    port = int(os.environ.get("PORT", 7860))  # Koyeb provides PORT
    server = HTTPServer(("0.0.0.0", port), SimpleHTTPRequestHandler)
    logging.info(f"✅ Health check server running on port {port}")
    server.serve_forever()
    threading.Thread(target=run_web, daemon=True).start()

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "Send me any Amazon/Flipkart link with text and I’ll fetch product image for you.\n\n"
        "Use /addchannel <channel_id> to set your posting channel.\n"
        "Use /redeem <coupon_code> to activate premium."
    )

# ---------------- COUPON (OWNER) ----------------
async def coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Owner command to generate coupons."""
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) != 3:
        await update.message.reply_text("Usage: /coupon <count> <validity_days> <plan_days>")
        return

    try:
        count = int(context.args[0])
        validity_days = int(context.args[1])
        plan_days = int(context.args[2])
    except ValueError:
        await update.message.reply_text("❌ Invalid arguments.")
        return

    created_on = now_ist()
    expiry = created_on + timedelta(days=validity_days)

    for i in range(count):
        code = f"CPN-{created_on.strftime('%d%m%H%M')}-{i}"
        msg = (
            "✅ Coupon Created\n"
            f"Code: `{code}`\n"
            f"Created on: {created_on.strftime('%d-%m-%Y %I:%M %p')} IST\n"
            f"Validity: {validity_days} days\n"
            f"Expiry: {expiry.strftime('%d-%m-%Y %I:%M %p')} IST\n"
            f"Plan Duration: {plan_days} days\n"
            f"Status: Not used"
        )
        await send_to_database(context, msg)
    await update.message.reply_text("✅ Coupons generated & saved in DB group.")

# ---------------- REDEEM ----------------
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User applies coupon."""
    if not context.args:
        await update.message.reply_text("Usage: /redeem <coupon_code>")
        return
    code = context.args[0].strip()

    # In real case: check from DB group if code exists, valid, unused
    # Here just mock logic
    created_on = now_ist()
    validity_days = 7
    expiry = created_on + timedelta(days=validity_days)

    msg = (
        "🎉 Congratulations your plan has been activated!\n"
        f"Name: {update.effective_user.first_name}\n"
        f"Date of activation: {created_on.strftime('%d-%m-%Y %I:%M %p')} IST\n"
        f"Validity: {validity_days} days\n"
        f"Date of expiry: {expiry.strftime('%d-%m-%Y %I:%M %p')} IST"
    )
    await update.message.reply_text(msg)

# ---------------- ADD CHANNEL ----------------
async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User adds channel for posting."""
    if not context.args:
        await update.message.reply_text("Usage: /addchannel <channel_id>")
        return
    channel_id = context.args[0]

    try:
        member = await context.bot.get_chat_member(channel_id, update.effective_user.id)
        if not member or member.status not in ["administrator", "creator"]:
            await update.message.reply_text(
                "❌ WE ARE UNABLE TO FIND YOUR CHANNEL KINDLY MAKE ME ADMIN OF YOUR CHANNEL"
            )
            return
    except Exception:
        await update.message.reply_text("❌ Kindly Recheck the channel id")
        return

    await send_to_database(context, f"USER {update.effective_user.id} CHANNEL {channel_id}")
    await update.message.reply_text("✅ Channel linked successfully!")

# ---------------- HANDLE LINKS ----------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # detect Amazon / Flipkart links
    links = [w for w in text.split() if "amzn.to" in w or "flipkart.com" in w]

    if len(links) == 0:
        return
    if len(links) > 1:
        await update.message.reply_text("❌ Many links in same message don't fetch images")
        return

    link = links[0]
    encoded = urllib.parse.quote(link)
    api_url = f"https://www.trackmyprice.in/api/getDetails?url={encoded}&refresh=false"

    try:
        r = requests.get(api_url, timeout=10).json()
        if "image" not in r or not r["image"]:
            await update.message.reply_text("❌ Kindly Recheck the product")
            return
        image_url = r["image"]
    except Exception:
        await update.message.reply_text("⚠️ Error fetching details")
        return

    # send image with same text
    await update.message.reply_photo(photo=image_url, caption=text)

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coupon", coupon))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(poll_interval=1, timeout=30)

if __name__ == "__main__":
    main()
    
