import telebot
from youtubesearchpython import VideosSearch
import os
import httpx
import re
import logging
import json
from flask import Flask
import threading

# -------------------------
# Config
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN", "8416104849:AAEV2neML_bs7L47zuymWHnnv6zWBsbtEd8")
OWNER_ID = int(os.getenv("OWNER_ID", 7588665244))
FORCE_CHANNEL = ""  # Leave empty to disable
DB_GROUP_ID = int(os.getenv("DB_GROUP_ID", -1002906782286)   # For storing songs
LOG_GROUP_ID = int(os.getenv("LOG_GROUP_ID", -1003150807266)  # For raw errors/logs
KVDB_BUCKET = os.getenv("KVDB_BUCKET", "C9CWKsR6fyceXoYfCGmDBy")
KVDB_BASE = f"https://kvdb.io/{KVDB_BUCKET}"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# -------------------------
# Global Data
# -------------------------
all_chats = set()
song_cache = {}  # url -> {'file_id': ..., 'title': ..., 'duration': ..., 'caption': ...}

# -------------------------
# Logging
# -------------------------
logging.basicConfig(filename="bot_errors.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------------
# KVDB Helpers
# -------------------------
def kvdb_set(key, value):
    try:
        httpx.put(f"{KVDB_BASE}/{key}", data=json.dumps(value))
    except Exception as e:
        logging.error(f"KVDB set error: {e}")

def kvdb_get(key):
    try:
        r = httpx.get(f"{KVDB_BASE}/{key}")
        if r.status_code == 200 and r.text.strip():
            return json.loads(r.text)
    except Exception as e:
        logging.error(f"KVDB get error: {e}")
    return None

def load_cache_from_kvdb():
    global song_cache
    cache = kvdb_get("song_cache")
    if cache:
        song_cache = cache

def save_cache_to_kvdb():
    kvdb_set("song_cache", song_cache)

# -------------------------
# Helpers
# -------------------------
def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def search_songs(query):
    results = VideosSearch(query + " song", limit=1).result()["result"]
    if not results:
        return None
    return {"title": results[0]["title"], "url": results[0]["link"], "duration": results[0].get("duration", "N/A")}

def download_song(url):
    if url in song_cache and 'file_path' in song_cache[url]:
        return song_cache[url]['file_path'], song_cache[url]['title'], song_cache[url]['duration']

    try:
        # Convert YouTube URL to Piped API
        video_id = url.split("v=")[-1]
        piped_api = f"https://piped.kavin.rocks/api/v1/videos/{video_id}"
        r = httpx.get(piped_api, timeout=10)
        r.raise_for_status()

        if not r.text.strip():
            raise ValueError(f"Piped API returned empty response for URL: {url}")

        data = r.json()

        title = sanitize_filename(data["title"])
        duration = data.get("length_seconds", 0)

        # Get best audio format URL
        audio_streams = [f for f in data["streams"] if f["type"].startswith("audio/")]
        best_audio = max(audio_streams, key=lambda x: x.get("bitrate", 0))
        audio_url = best_audio["url"]

        # Download audio
        file_path = f"{title}.m4a"
        with httpx.stream("GET", audio_url, timeout=60) as stream:
            with open(file_path, "wb") as f:
                for chunk in stream.iter_bytes(chunk_size=1024*1024):
                    f.write(chunk)

        song_cache[url] = {'file_path': file_path, 'title': title, 'duration': duration}
        save_cache_to_kvdb()
        return file_path, title, duration

    except Exception as e:
        logging.error(f"Piped download error: {e}")
        raise

def check_force_channel(user_id):
    if not FORCE_CHANNEL:
        return True
    try:
        member = bot.get_chat_member(FORCE_CHANNEL, user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
        return False
    except:
        return False

def handle_error(chat_id, e):
    bot.send_message(chat_id, "❌ Something went wrong while processing your request. Please try again later.")
    try:
        bot.send_message(LOG_GROUP_ID, f"⚠️ Error for chat {chat_id}:\n`{e}`")
    except Exception as log_err:
        logging.error(f"Failed to send error to LOG group: {log_err}")

def send_song_to_user_and_db(chat_id, song_url):
    try:
        file_path, title, duration = download_song(song_url)
        caption = (
            f"🎵 Title : {title}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"⏱ Duration : {duration//60}:{duration%60:02d}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            "Made with love by [Smart Tg Bots](https://t.me/SmartTgBots)"
        )

        with open(file_path, "rb") as audio:
            db_msg = bot.send_audio(DB_GROUP_ID, audio, caption=caption)
            song_cache[song_url]['file_id'] = db_msg.audio.file_id
            song_cache[song_url]['caption'] = caption
            save_cache_to_kvdb()

        with open(file_path, "rb") as audio:
            bot.send_audio(chat_id, audio, title=title, caption=caption)

        os.remove(file_path)
    except Exception as e:
        handle_error(chat_id, e)

# -------------------------
# Command Handlers
# -------------------------
@bot.message_handler(commands=["start"])
def start(msg):
    all_chats.add(msg.chat.id)
    bot.send_message(
        msg.chat.id,
        "🎵 I'm a Music Downloader Bot!\n\n"
        "Send me the name of the song, and I will fetch it for you automatically.\n"
        "Example: Hanumankind\n\n"
        "Made by [Smart Tg Bots](https://t.me/SmartTgBots)"
    )

@bot.message_handler(commands=["stats"])
def stats(msg):
    if msg.from_user.id != OWNER_ID:
        return bot.reply_to(msg, "⛔ You're not allowed.")
    bot.send_message(msg.chat.id, f"👥 Total chats/users: {len(all_chats)}")

# -------------------------
# Automatic Song Download Handler
# -------------------------
@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    all_chats.add(msg.chat.id)
    try:
        text = msg.text.strip()
        if not text:
            return bot.send_message(msg.chat.id, "❌ Please send a valid song name.")

        if not check_force_channel(msg.from_user.id):
            return bot.send_message(msg.chat.id, f"⚠️ You must join {FORCE_CHANNEL} first!")

        searching_msg = bot.send_message(msg.chat.id, "🔍 Searching for your song...")
        song = search_songs(text)
        bot.delete_message(msg.chat.id, searching_msg.message_id)

        if not song:
            return bot.send_message(msg.chat.id, "❌ No results found.")

        downloading_msg = bot.send_message(msg.chat.id, f"⬇️ Downloading: {song['title']}...")
        send_song_to_user_and_db(msg.chat.id, song['url'])
        bot.delete_message(msg.chat.id, downloading_msg.message_id)

    except Exception as e:
        logging.error(f"Error handling message: {e}")
        handle_error(msg.chat.id, e)

# -------------------------
# Load cache & run bot
# -------------------------
load_cache_from_kvdb()
print("✅ Bot is running...")
bot.infinity_polling()

# -------------------------
# Flask keep-alive for Railway
# -------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Music Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()
