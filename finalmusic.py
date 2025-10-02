import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from youtubesearchpython import VideosSearch
import yt_dlp
import os
import httpx
import re
import logging
import json

# -------------------------
# Config (Insert your own secrets here)
# -------------------------
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
OWNER_ID = 7588665244
FORCE_CHANNEL = ""  # Leave empty to disable
DB_GROUP_ID = -1002906782286  # Replace with your database group ID

KVDB_BUCKET = "C9CWKsR6fyceXoYfCGmDBy"
KVDB_BASE = f"https://kvdb.io/{KVDB_BUCKET}"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# -------------------------
# Global Data
# -------------------------
search_results = {}  # chat_id -> search results
current_messages = {}  # chat_id -> list of message IDs
all_chats = set()  # track all users/chats
song_cache = {}  # url -> {'file_id': ..., 'title': ..., 'duration': ..., 'caption': ...}

# -------------------------
# Logging
# -------------------------
logging.basicConfig(filename="bot_errors.log", level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# -------------------------
# Monkey-patch httpx to ignore proxies
# -------------------------
original_post = httpx.post
def patched_post(*args, **kwargs):
    kwargs.pop("proxies", None)
    return original_post(*args, **kwargs)
httpx.post = patched_post

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
        if r.status_code == 200 and r.text != "":
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
    results = VideosSearch(query + " song", limit=5).result()["result"]
    return [{"title": r["title"], "url": r["link"], "duration": r.get("duration", "N/A")} for r in results]

def download_song(url):
    if url in song_cache and 'file_path' in song_cache[url]:
        return song_cache[url]['file_path'], song_cache[url]['title'], song_cache[url]['duration']
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "%(title).40s.%(ext)s",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = sanitize_filename(ydl.prepare_filename(info))
        if filename.endswith((".webm", ".m4a")):
            filename = filename.rsplit(".", 1)[0] + ".m4a"
    song_cache[url] = {'file_path': filename, 'title': info.get("title", "Unknown"), 'duration': info.get("duration", 0)}
    save_cache_to_kvdb()  # Save after download
    return filename, info.get("title", "Unknown"), info.get("duration", 0)

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

def send_song_to_user_and_db(chat_id, song_url, yt_url=None):
    # Download
    file_path, title, duration = download_song(song_url)

    # Unified caption
    caption = (
        f"(Music)\n"
        f"🎵 Title : {title}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"⏱ Duration : {duration//60}:{duration%60:02d}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        "Made with love by [Smart Tg Bots](https://t.me/SmartTgBots)"
    )

    # Inline keyboard
    kb = InlineKeyboardMarkup()
    if yt_url:
        kb.add(InlineKeyboardButton("🎵 Listen Now", url=yt_url))
    kb.add(InlineKeyboardButton("💬 Support", url="https://t.me/Smarttgsupportbot"))
    kb.add(InlineKeyboardButton("📣 Updates", url="https://t.me/SmartTgBots"))

    # Send to DB group
    with open(file_path, "rb") as audio:
        db_msg = bot.send_audio(DB_GROUP_ID, audio, caption=caption, reply_markup=kb)
        song_cache[song_url]['file_id'] = db_msg.audio.file_id
        song_cache[song_url]['caption'] = caption
        save_cache_to_kvdb()

    # Send to user
    with open(file_path, "rb") as audio:
        bot.send_audio(chat_id, audio, title=title, caption=caption, reply_markup=kb)

    # Delete local file
    os.remove(file_path)

# -------------------------
# Command Handlers
# -------------------------
@bot.message_handler(commands=["start"])
def start(msg):
    all_chats.add(msg.chat.id)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("➕ Add Me", url="http://t.me/SongsDownload_Robot?startgroup=true"))
    kb.add(InlineKeyboardButton("💬 Support", url="http://t.me/Smarttgsupportbot"))
    kb.add(InlineKeyboardButton("📣 Updates", url="http://t.me/SmartTgBots"))
    kb.add(InlineKeyboardButton("❓ Help", callback_data="help"))
    bot.send_message(
        msg.chat.id,
        "🎵 I'm a Music Downloader Bot!\n\n"
        "Send me the name of song you want to download and see the magic.\n"
        "Example - Hanumankind\n\n"
        "Use me in groups too by typing:\n"
        "`@SongsDownload_Robot song name`\n\n"
        "Made by [Smart Tg Bots](https://t.me/SmartTgBots)",
        reply_markup=kb
    )

@bot.message_handler(commands=["help"])
def help_command(msg):
    bot.send_message(
        msg.chat.id,
        "🎵 **Music Downloader Bot Help**\n\n"
        "• Send me the name of any song and I will fetch it for you.\n"
        "• Use inline queries in groups: `@SongsDownload_Robot song name`\n"
        "• Only the owner can use /stats to see total users.\n"
        "• Songs you request are cached in the database group for future requests."
    )

@bot.message_handler(commands=["stats"])
def stats(msg):
    if msg.from_user.id != OWNER_ID:
        return bot.reply_to(msg, "⛔ You're not allowed.")
    bot.send_message(msg.chat.id, f"👥 Total chats/users: {len(all_chats)}")

# -------------------------
# Message Handler
# -------------------------
@bot.message_handler(func=lambda m: True)
def handle_message(msg):
    all_chats.add(msg.chat.id)
    text = msg.text.strip()
    if not text:
        return bot.send_message(msg.chat.id, "❌ Please send a valid song name.")
    if msg.chat.type in ["group", "supergroup"]:
        if not text.lower().startswith(f"@{bot.get_me().username.lower()}"):
            return
        text = text.split(" ", 1)[1] if " " in text else ""
        if not text:
            return
    if not check_force_channel(msg.from_user.id):
        return bot.send_message(msg.chat.id, f"⚠️ You must join {FORCE_CHANNEL} first!")

    # Searching message
    searching_msg = bot.send_message(msg.chat.id, "🔍 Searching...")
    current_messages[msg.chat.id] = [searching_msg.message_id]

    try:
        results = search_songs(text)
        if not results:
            bot.delete_message(msg.chat.id, searching_msg.message_id)
            return bot.send_message(msg.chat.id, "❌ No results found.")
        search_results[msg.chat.id] = results

        kb = InlineKeyboardMarkup()
        for i, r in enumerate(results):
            kb.add(InlineKeyboardButton(f"{i+1}. {r['title'][:40]} ⏱ {r['duration']}", callback_data=str(i)))

        choices_msg = bot.send_message(msg.chat.id, "✅ Choose a song:", reply_markup=kb)
        current_messages[msg.chat.id].append(choices_msg.message_id)
        bot.delete_message(msg.chat.id, searching_msg.message_id)
    except Exception as e:
        logging.error(f"Error searching: {e}")
        bot.send_message(msg.chat.id, f"⚠️ Error: {e}")

# -------------------------
# Callback Query Handler
# -------------------------
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    try:
        index = int(call.data)
        song = search_results[chat_id][index]

        # Delete previous messages
        for mid in current_messages.get(chat_id, []):
            try: bot.delete_message(chat_id, mid)
            except: pass
        current_messages[chat_id] = []

        downloading_msg = bot.send_message(chat_id, f"⬇️ Downloading: {song['title']}...")
        current_messages[chat_id].append(downloading_msg.message_id)

        # Instant delivery if in cache
        if song['url'] in song_cache and 'file_id' in song_cache[song['url']]:
            kb = InlineKeyboardMarkup()
            if song['url']:
                kb.add(InlineKeyboardButton("🎵 Listen Now", url=song['url']))
            kb.add(InlineKeyboardButton("💬 Support", url="https://t.me/Smarttgsupportbot"))
            kb.add(InlineKeyboardButton("📣 Updates", url="https://t.me/SmartTgBots"))

            bot.send_audio(
                chat_id,
                song_cache[song['url']]['file_id'],
                caption=song_cache[song['url']]['caption'],
                reply_markup=kb
            )
        else:
            send_song_to_user_and_db(chat_id, song['url'], song['url'])

        bot.delete_message(chat_id, downloading_msg.message_id)
        del search_results[chat_id]
    except Exception as e:
        logging.error(f"Callback error: {e}")
        bot.send_message(chat_id, f"❌ Error: {e}")

# -------------------------
# Load cache & run bot
# -------------------------
load_cache_from_kvdb()
print("✅ Bot is running...")
bot.infinity_polling()

# -------------------------
# Flask keep-alive for Railway
# -------------------------
from flask import Flask
import threading

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Music Bot is running!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()