from flask import Flask, request
import requests
import time
import urllib.parse
import threading

app = Flask(__name__)

# Owner + Telegram details
BOT_TOKEN = "7616827659:AAFAUxnF1xfiByHaxoC0pUVPX0pPkO45OPQ"
OWNER_ID = "7588665244"

# In-memory users dict (username: {expiry, msg_id, request_count})
users = {}

# SiteStripe cookies (your working cookie)
COOKIES = (
    "session-id=258-2488057-5180660; "
    "i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
    "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d-...; "
    'sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; '
    "sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7d4sk...; "
    "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndzFtanm3...;"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Cookie": COOKIES
}

def send_dm(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    return requests.post(url, data={"chat_id": OWNER_ID, "text": text}).json()

def edit_dm(msg_id, new_text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    requests.post(url, data={"chat_id": OWNER_ID, "message_id": msg_id, "text": new_text})

def auto_expiry_checker():
    while True:
        time.sleep(30)
        now = int(time.time())
        expired = [u for u, d in users.items() if now > d["expiry"]]
        for u in expired:
            try:
                edit_dm(users[u]["msg_id"], f"🚫 User `{u}` expired.")
            except: pass
            del users[u]

threading.Thread(target=auto_expiry_checker, daemon=True).start()

@app.route("/")
def index():
    return "✅ Amazon Shortener API Live"

@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    days = request.args.get("days")

    if secret != "ayusar@2010" or not user or not days:
        return "❌ Unauthorized or missing params", 403

    expiry = int(time.time()) + int(days) * 86400
    msg = send_dm(f"✅ User `{user}` added.\nRequests: 0\nValid for: {days} days")
    users[user] = {"expiry": expiry, "msg_id": msg["result"]["message_id"], "request_count": 0}
    return "✅ User added"

@app.route("/api")
def shortener():
    user = request.args.get("api")
    long_url = request.args.get("link")

    if not user or user not in users:
        return "❌ Invalid or unauthorized API", 403

    if time.time() > users[user]["expiry"]:
        edit_dm(users[user]["msg_id"], f"🚫 User `{user}` expired.")
        del users[user]
        return "❌ Expired access", 403

    if "amazon." not in long_url:
        return "❌ Invalid Amazon link", 400

    encoded = urllib.parse.quote_plus(long_url)
    r = requests.get(f"https://www.amazon.in/associates/sitestripe/getShortUrl?longUrl={encoded}&marketplaceId=44571", headers=HEADERS)

    users[user]["request_count"] += 1
    try:
        edit_dm(users[user]["msg_id"],
            f"✅ User `{user}`\nRequests: {users[user]['request_count']}\nValid till: {time.strftime('%d-%m-%Y %H:%M', time.localtime(users[user]['expiry']))}"
        )
    except: pass

    if r.status_code == 200:
        return r.json().get("shortUrl", "❌ Error: No short URL")
    else:
        return f"❌ Amazon Error {r.status_code}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
