# om ganesha namah
# Jai shree krishna 
import logging
import os
import random
import string
import asyncio
from datetime import datetime, timedelta
from io import BytesIO

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from pyppeteer import launch
from flask import Flask

# ---------------- CONFIG ---------------- #
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
OWNER_ID = 7588665244
GROUP_ID = -1002906782286

# ---------------------------------------- #
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (synced with group messages)
coupons = {}
user_plans = {}

# ---------------- UTILS ---------------- #
def generate_coupon_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def now_ist():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def is_premium(user_id: int):
    if user_id in user_plans:
        return user_plans[user_id] > now_ist()
    return False

# ---------------- BOT HANDLERS ---------------- #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a link and I'll capture a screenshot. If you have a coupon, use /redeem <coupon>.")

# Owner: Generate coupons
async def coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ You are not allowed.")

    try:
        count = int(context.args[0])
        validity_days = int(context.args[1])
        plan_days = int(context.args[2])
    except:
        return await update.message.reply_text("Usage: /coupon <count> <validity_days> <plan_days>")

    coupons_created = []
    for _ in range(count):
        code = generate_coupon_code()
        expiry = now_ist() + timedelta(days=validity_days)
        coupons[code] = {"expiry": expiry, "plan_days": plan_days, "used": False}
        coupons_created.append(code)

    msg = f"🎟 Generated {count} coupons (valid {validity_days}d, plan {plan_days}d):\n" + "\n".join(coupons_created)
    await update.message.reply_text(msg)
    # log to group
    await context.bot.send_message(GROUP_ID, f"[COUPON LOG]\n{msg}")

# Redeem coupon
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Usage: /redeem <coupon_code>")

    code = context.args[0].strip().upper()
    if code not in coupons:
        return await update.message.reply_text("❌ Invalid coupon.")
    
    data = coupons[code]
    if data["used"]:
        return await update.message.reply_text("❌ Coupon already used.")
    if now_ist() > data["expiry"]:
        return await update.message.reply_text("❌ Coupon expired.")

    # Assign premium
    user_plans[update.effective_user.id] = now_ist() + timedelta(days=data["plan_days"])
    coupons[code]["used"] = True

    expiry = user_plans[update.effective_user.id].strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"✅ Coupon redeemed! Premium active until {expiry} (IST)")
    await context.bot.send_message(GROUP_ID, f"[REDEEM LOG] User {update.effective_user.id} redeemed {code}, valid until {expiry}")

# Screenshot capture
async def capture_screenshot(url: str):
    browser = await launch(headless=True, args=["--no-sandbox"])
    page = await browser.newPage()
    await page.goto(url, {"waitUntil": "networkidle2"})
    screenshot = await page.screenshot(fullPage=True)
    await browser.close()
    return screenshot

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not text.startswith("http"):
        return await update.message.reply_text("❌ Please send a valid link.")

    if not is_premium(user_id):
        return await update.message.reply_text("🔒 You need premium to use this feature. Redeem with /redeem <coupon>.")

    await update.message.reply_text("⏳ Fetching screenshot, please wait...")

    try:
        screenshot = await capture_screenshot(text)
        await update.message.reply_photo(photo=BytesIO(screenshot), caption="📸 Screenshot captured!")
        await context.bot.send_message(GROUP_ID, f"[SCREENSHOT LOG] User {user_id} captured {text}")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Failed to capture screenshot.")

# ---------------- DUMMY SERVER ---------------- #
server = Flask(__name__)

@server.route("/")
def health():
    return "OK", 200

# ---------------- MAIN ---------------- #
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coupon", coupon))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

    # Run both bot + server
    loop = asyncio.get_event_loop()
    loop.create_task(app.run_polling(poll_interval=30))
    server.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
