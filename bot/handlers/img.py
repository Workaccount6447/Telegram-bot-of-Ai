import json
import time
from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp
from config import OWNER_ID, HUGGINGFACE_API_KEY

USAGE_FILE = "bot/usage_limits.json"

def load_usage():
    try:
        with open(USAGE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_usage(usage):
    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)

@dp.message_handler(Command("img"))
async def generate_image(message: types.Message):
    user_id = str(message.from_user.id)
    if str(user_id) != str(OWNER_ID):
        usage = load_usage()
        today = str(int(time.time()) // 86400)
        if user_id not in usage:
            usage[user_id] = {}
        if usage[user_id].get("day") != today:
            usage[user_id] = {"day": today, "img": 0, "sum": 0}
        if usage[user_id]["img"] >= 5:
            await message.reply("⚠️ Daily image generation limit reached (5 per day). Please try again tomorrow.")
            return
        usage[user_id]["img"] += 1
        save_usage(usage)

    prompt = message.get_args()
    if not prompt:
        await message.reply("Please provide a prompt. Usage: /img <prompt>")
        return

    await message.reply("Generating image...")

    import requests
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    payload = {
        "inputs": prompt
    }
    response = requests.post("https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0", headers=headers, json=payload)
    if response.status_code == 200:
        await message.reply_photo(photo=response.content)
    else:
        await message.reply("Failed to generate image. Please try again later.")