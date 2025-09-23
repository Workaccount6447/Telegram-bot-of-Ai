# om ganesha namah
# Jai shree krishna 

import logging
import socket
import threading
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ================== CONFIG ==================
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
OWNER_ID = 7588665244
GROUP_ID = -1002906782286
# ============================================

# Store coupons and user activations
coupons = {}
user_data = {}

logging.basicConfig(level=logging.INFO)


# ----------------- HEALTH SERVER -----------------
def run_health_server():
    """Runs a dummy TCP server for health checks"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 8080))  # listen on port 8080
    server_socket.listen(1)
    logging.info("Health check server running on port 8080")

    while True:
        client_socket, addr = server_socket.accept()
        client_socket.send(b"OK\n")
        client_socket.close()


threading.Thread(target=run_health_server, daemon=True).start()
# -------------------------------------------------


# ---------------- BOT HANDLERS -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📸 Send me a photo and I will capture/store it.\n"
        "Use a coupon code with /redeem <coupon> to activate your plan."
    )


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id not in user_data:
        await update.message.reply_text("❌ You don’t have an active plan. Please redeem a coupon.")
        return

    expiry = user_data[user.id]["expiry"]
    if datetime.now() > expiry:
        await update.message.reply_text("⚠️ Your premium plan has expired.")
        return

    # Forward photo to group (acting as DB)
    file_id = update.message.photo[-1].file_id
    await context.bot.send_photo(chat_id=GROUP_ID, photo=file_id, caption=f"From: {user.full_name} ({user.id})")

    await update.message.reply_text("✅ Photo captured and stored.")


async def generate_coupons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if len(context.args) != 3:
        await update.message.reply_text("Usage: /coupon <count> <validity_days> <plan_days>")
        return

    count = int(context.args[0])
    validity_days = int(context.args[1])
    plan_days = int(context.args[2])

    generated = []
    for i in range(count):
        code = f"COUPON{i+1}_{int(datetime.now().timestamp())}"
        expiry = datetime.now() + timedelta(days=validity_days)
        coupons[code] = {"valid_until": expiry, "plan_days": plan_days}
        generated.append(code)

    await update.message.reply_text(
        "🎟 Coupons Generated (use `/redeem <code>`):\n" + "\n".join(f"`{c}`" for c in generated),
        parse_mode="Markdown",
    )


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /redeem <coupon>")
        return

    code = context.args[0]
    if code not in coupons:
        await update.message.reply_text("❌ Invalid coupon.")
        return

    coupon = coupons.pop(code)  # one-time use
    if datetime.now() > coupon["valid_until"]:
        await update.message.reply_text("⚠️ This coupon has expired.")
        return

    expiry = datetime.now() + timedelta(days=coupon["plan_days"])
    user_data[update.effective_user.id] = {
        "name": update.effective_user.full_name,
        "activated": datetime.now(),
        "expiry": expiry,
        "plan_days": coupon["plan_days"],
    }

    # Send to group (acting as DB)
    await context.bot.send_message(
        GROUP_ID,
        f"👤 Name: {update.effective_user.full_name}\n"
        f"🗓 Activated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"⏳ Validity: {coupon['plan_days']} days\n"
        f"📅 Expiry: {expiry.strftime('%Y-%m-%d %H:%M:%S')}",
    )

    await update.message.reply_text(
        f"✅ Coupon redeemed!\n"
        f"Plan active for {coupon['plan_days']} days.\n"
        f"Expiry: {expiry.strftime('%Y-%m-%d %H:%M:%S')}"
    )


# ----------------- MAIN -----------------
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coupon", generate_coupons))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))

    app.run_polling(poll_interval=30)  # <- 30 seconds


if __name__ == "__main__":
    main()
