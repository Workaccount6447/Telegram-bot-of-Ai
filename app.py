# om ganesha namah
# Jai shree krishna 
import os
import re
import json
import logging
import requests
import threading
import socket
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ================= CONFIG =================
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
OWNER_ID = 7588665244
GROUP_ID = -1002906782286
# ==========================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# "Database" simulated with dicts
coupons = {}      # coupon -> {plan_days, used}
user_plans = {}   # user_id -> {expiry, activated_on}

# ---------------- UTILITIES ----------------
def now_ist():
    return datetime.utcnow() + timedelta(hours=5, minutes=30)

def encode_url(url: str) -> str:
    return requests.utils.quote(url, safe="")

def fetch_product_image(link: str):
    """Fetch product image URL from TrackMyPrice API"""
    api_url = f"https://www.trackmyprice.in/api/getDetails?url={encode_url(link)}&refresh=false"
    resp = requests.get(api_url, timeout=15)
    if resp.status_code != 200:
        return None
    try:
        data = resp.json()
        return data.get("image")
    except Exception:
        return None

def run_health_server():
    """Dummy TCP server for health checks on port 8080"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 8080))
    server.listen(5)
    logger.info("Health check server running on port 8080")
    while True:
        conn, _ = server.accept()
        conn.sendall(b"OK")
        conn.close()

# ---------------- HANDLERS -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_plans or user_plans[user_id]["expiry"] < now_ist():
        await update.message.reply_text(
            "You are not authorised to use this bot.\nSupport - @support"
        )
    else:
        expiry = user_plans[user_id]["expiry"].strftime("%Y-%m-%d %H:%M:%S")
        await update.message.reply_text(f"Welcome back premium user!\nYour plan expires on {expiry}")

async def generate_coupons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    try:
        num = int(context.args[0])
        plan_days = int(context.args[1])
    except:
        await update.message.reply_text("Usage: /coupon <number> <plan_days>")
        return

    import secrets
    out = []
    for _ in range(num):
        cpn = secrets.token_hex(4)
        coupons[cpn] = {"plan_days": plan_days, "used": False}
        out.append(cpn)

    await update.message.reply_text("Generated coupons:\n" + "\n".join(out))

async def add_plan_by_coupon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /addplanbycoupon <coupon>")
        return
    cpn = context.args[0]
    if cpn not in coupons or coupons[cpn]["used"]:
        await update.message.reply_text("Invalid or already used coupon.")
        return

    plan_days = coupons[cpn]["plan_days"]
    coupons[cpn]["used"] = True
    expiry = now_ist() + timedelta(days=plan_days)
    user_plans[update.effective_user.id] = {
        "activated_on": now_ist(),
        "expiry": expiry,
    }
    await update.message.reply_text(
        f"🎉 Congratulations your plan has been activated!\n"
        f"Validity: {plan_days} days\n"
        f"Expiry: {expiry.strftime('%Y-%m-%d %H:%M:%S')}"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_plans or user_plans[user_id]["expiry"] < now_ist():
        await update.message.reply_text("You are not authorised to use this bot.\nSupport - @support")
        return

    text = update.message.text or ""
    links = re.findall(r"(https?://\S+)", text)

    if len(links) == 0:
        return
    if len(links) > 1:
        await update.message.reply_text("Many links in same message don't fetch images")
        return

    link = links[0]
    await update.message.reply_text("⏳ Fetching product image...")

    img_url = fetch_product_image(link)
    if not img_url:
        await update.message.reply_text("Kindly Recheck the product")
        return

    try:
        await update.message.reply_photo(
            photo=img_url,
            caption=text
        )
    except Exception as e:
        await update.message.reply_text(f"Error sending image: {e}")

# ---------------- MAIN ---------------------
def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coupon", generate_coupons))
    app.add_handler(CommandHandler("addplanbycoupon", add_plan_by_coupon))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(poll_interval=30)

if __name__ == "__main__":
    main()
