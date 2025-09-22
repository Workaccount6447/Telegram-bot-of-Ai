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
import json
import asyncio

# ---------------- CONFIG ----------------
BOT_TOKEN = "8369123404:AAG_pWjtGOub0DBYEDbCE6-wuR3zol_KWNU"
OWNER_ID = 7588665244
DATABASE_GROUP_ID = -1002906782286  # group used as database

# In-memory dictionaries to store data from the DB group
user_channels = {}
generated_coupons = {}
redeemed_coupons = {}
bot_starters = set()

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

async def load_data_from_db_group(context: ContextTypes.DEFAULT_TYPE):
    """Loads bot state from the database group history."""
    logging.info("⏳ Loading data from database group...")
    try:
        async for message in context.bot.get_chat_history(chat_id=DATABASE_GROUP_ID):
            text = message.text
            if not text:
                continue
            
            # Load user start data
            if "USER STARTED BOT" in text:
                user_id_str = text.split("ID: ")[-1].strip()
                if user_id_str.isdigit():
                    bot_starters.add(int(user_id_str))
            
            # Load linked channel data
            elif "LINKED CHANNEL" in text:
                parts = text.split("CHANNEL")
                user_id_str = parts[0].split("USER")[-1].strip()
                channel_id = parts[-1].strip()
                if user_id_str.isdigit():
                    user_channels[int(user_id_str)] = channel_id
            
            # Load coupon data
            elif "✅ Coupon Created" in text:
                try:
                    code = text.split("Code: `")[-1].split("`")[0].strip()
                    expiry_str = text.split("Expiry: ")[-1].split(" IST")[0].strip()
                    plan_days = int(text.split("Plan Duration: ")[-1].split(" ")[0])
                    generated_coupons[code] = {
                        "expiry": datetime.strptime(expiry_str, '%d-%m-%Y %I:%M %p'),
                        "plan_days": plan_days,
                        "status": "Not used" # Assume not used until proven otherwise
                    }
                except (ValueError, IndexError):
                    logging.warning(f"Could not parse coupon creation message: {text}")
            
            # Load redeemed coupon data
            elif "🎉 CONGRATS" in text:
                try:
                    code = text.split("Code: `")[-1].split("`")[0].strip()
                    user_id_str = text.split("Redeemed by User ID: ")[-1].split("\n")[0]
                    if code in generated_coupons:
                        generated_coupons[code]["status"] = "Used"
                    if user_id_str.isdigit():
                        redeemed_coupons[code] = int(user_id_str)
                except (ValueError, IndexError):
                    logging.warning(f"Could not parse coupon redemption message: {text}")
                    
    except Exception as e:
        logging.error(f"Failed to load data from database group: {e}")

    logging.info("✅ Data loaded successfully.")
    logging.info(f"Loaded {len(bot_starters)} unique bot starters.")
    logging.info(f"Loaded {len(user_channels)} linked channels.")
    logging.info(f"Loaded {len(generated_coupons)} generated coupons.")
    logging.info(f"Loaded {len(redeemed_coupons)} redeemed coupons.")

# Start the web server in a background daemon thread
threading.Thread(target=run_web, daemon=True).start()

# ---------------- COMMANDS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in bot_starters:
        bot_starters.add(user_id)
        await send_to_database(context, f"USER STARTED BOT | ID: {user_id}")
    
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\n\n"
        "Send me any Amazon/Flipkart link with text and I’ll fetch product image for you.\n\n"
        "Use /addchannel <channel_id> to set your posting channel.\n"
        "Use /redeem <coupon_code> to activate premium."
    )

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
        generated_coupons[code] = {
            "expiry": expiry,
            "plan_days": plan_days,
            "status": "Not used"
        }
        await send_to_database(context, msg)
    await update.message.reply_text(f"✅ {count} coupons generated & saved in DB group.")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User applies coupon."""
    if not context.args:
        await update.message.reply_text("Usage: /redeem <coupon_code>")
        return
    
    code = context.args[0].strip()
    user_id = update.effective_user.id

    if code not in generated_coupons:
        await update.message.reply_text("❌ Invalid coupon code.")
        return
    
    coupon_data = generated_coupons[code]
    
    if coupon_data["status"] == "Used" or code in redeemed_coupons:
        await update.message.reply_text("❌ This coupon has already been used.")
        return
    
    if now_ist() > coupon_data["expiry"]:
        await update.message.reply_text("❌ This coupon has expired.")
        return
    
    coupon_data["status"] = "Used"
    redeemed_coupons[code] = user_id

    msg = (
        "🎉 CONGRATS, YOUR PLAN HAS BEEN ACTIVATED!\n"
        f"Code: `{code}`\n"
        f"Redeemed by User ID: {user_id}\n"
        f"Name: {update.effective_user.first_name}\n"
        f"Date of activation: {now_ist().strftime('%d-%m-%Y %I:%M %p')} IST\n"
        f"Plan Duration: {coupon_data['plan_days']} days\n"
        f"Date of expiry: {(now_ist() + timedelta(days=coupon_data['plan_days'])).strftime('%d-%m-%Y %I:%M %p')} IST"
    )
    await send_to_database(context, msg)
    await update.message.reply_text(msg)

async def addchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """User adds channel for posting."""
    if not context.args:
        await update.message.reply_text("Usage: /addchannel <channel_id>")
        return
    channel_id = context.args[0]
    user_id = update.effective_user.id

    try:
        member = await context.bot.get_chat_member(channel_id, user_id)
        if not member or member.status not in ["administrator", "creator"]:
            await update.message.reply_text(
                "❌ I am unable to find your channel or am not an admin in it. Please make me an administrator and re-try."
            )
            return
    except Exception:
        await update.message.reply_text("❌ Kindly Recheck the channel ID")
        return

    user_channels[user_id] = channel_id
    await send_to_database(context, f"USER {user_id} LINKED CHANNEL {channel_id}")
    await update.message.reply_text("✅ Channel linked successfully!")

# ---------------- CORE LOGIC ---------------

# Corrected code
def handle_message(update, context):
    if update.message is not None and update.message.text is not None:
        text = update.message.text
        # Now you can safely process the text message
        # rest of your code here
    else:
        # This block handles non-text updates, like photos, stickers, or new members.
        # You can add logic here to respond differently or do nothing.
        print("Received a non-text update.")
        # Example: send a friendly message back to the user
        # update.message.reply_text("I can only process text messages right now. 😅")

    user_id = update.effective_user.id
    
    links = [w for w in text.split() if "amzn.to" in w or "flipkart.com" in w]

    if not links:
        return
    if len(links) > 1:
        await
        update.message.reply_text("❌ Please send only one link per message.")
        return

    link = links[0]
    
    try:
        url1 = "https://flipshope.com/api/prices/finalfetchurl"
        payload1 = {"url": link}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
        
        r1 = requests.post(url1, json=payload1, headers=headers, timeout=10)
        r1.raise_for_status()
        data1 = r1.json()
        
        if "data" not in data1 or not data1["data"]:
            await update.message.reply_text("❌ Could not get data link from API. Please re-check the product.")
            return

        data_url = data1["data"]
        
        url2 = "https://flipshope.com/api/prices/getsidpid"
        payload2 = {"link": data_url}
        r2 = requests.post(url2, json=payload2, headers=headers, timeout=10)
        r2.raise_for_status()
        data2 = r2.json()

        if "pid" not in data2 or not data2["pid"]:
            await update.message.reply_text("❌ Could not get product ID from API.")
            return

        pid = data2["pid"]
        
        url3 = f"https://buyhatke.com/api/productData?pos=2&pid={pid}"
        r3 = requests.get(url3, timeout=10)
        r3.raise_for_status()
        data3 = r3.json()
        
        if "image" not in data3 or not data3["image"]:
            await update.message.reply_text("❌ No image found in the product data.")
            return

        image_url = data3["image"]
        
        channel_id = user_channels.get(user_id)
        
        if channel_id:
            try:
                await context.bot.send_photo(
                    chat_id=channel_id,
                    photo=image_url,
                    caption=text
                )
                await update.message.reply_text("✅ Product image forwarded to your linked channel!")
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to forward to channel. Error: {e}")
        else:
            await update.message.reply_text(
                "✅ Image fetched! Please use /addchannel to set your posting channel if you want me to forward it."
            )
            await update.message.reply_photo(photo=image_url, caption=text)
            
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        await update.message.reply_text("⚠️ An error occurred while fetching product details. Please try again later.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text("❌ An unexpected error occurred. Kindly re-check the product.")

# ---------------- MAIN ----------------
async def post_init(application: Application):
    """Load data from the database group before starting the bot."""
    await load_data_from_db_group(application)

def main():
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("coupon", coupon))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("addchannel", addchannel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling(poll_interval=1, timeout=30)

if __name__ == "__main__":
    main()

