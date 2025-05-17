import json
import time
from aiogram import types
from aiogram.dispatcher.filters import Command
from bot import dp
from config import OWNER_ID, RAPIDAPI_KEY

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

@dp.message_handler(Command("summarise"))
async def summarise_video(message: types.Message):
    user_id = str(message.from_user.id)
    if str(user_id) != str(OWNER_ID):
        usage = load_usage()
        today = str(int(time.time()) // 86400)
        if user_id not in usage:
            usage[user_id] = {}
        if usage[user_id].get("day") != today:
            usage[user_id] = {"day": today, "img": 0, "sum": 0}
        if usage[user_id]["sum"] >= 5:
            await message.reply("⚠️ Daily summary limit reached (5 per day). Please try again tomorrow.")
            return
        usage[user_id]["sum"] += 1
        save_usage(usage)

    link = message.get_args().strip()
    if not link:
        await message.reply("Please provide a YouTube link. Usage: /summarise <link>")
        return

    await message.reply("Summarizing video...")

    import requests
    url = "https://youtube-transcriptor.p.rapidapi.com/transcript"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "youtube-transcriptor.p.rapidapi.com"
    }
    response = requests.post(url, json={"url": link}, headers=headers)
    if response.status_code == 200:
        result = response.json()
        summary = result.get("summary") or "Summary not available."
        await message.reply(summary)
    else:
        await message.reply("Failed to summarize the video. Please try again later.")