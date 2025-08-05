from flask import Flask, request
import requests
import urllib.parse
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB setup
mongo_uri = "mongodb+srv://telegrambot:ayusar%402010@cluster0.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["shortener"]
users = db["users"]

# Flask app
app = Flask(__name__)

# Amazon SiteStripe Cookie (WORKING)
COOKIES = (
    "session-id=258-2488057-5180660; "
    "i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
    "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d...; "
    'sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; '
    "sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7d4sk...; "
    "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndzFtanm3..."
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": COOKIES
}

@app.route("/")
def home():
    return "✅ Amazon Shortener API is Live"

@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    days = request.args.get("days")

    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403

    try:
        days = int(days)
    except:
        return "❌ Invalid 'days' value", 400

    expiry = datetime.utcnow() + timedelta(days=days)

    users.update_one(
        {"api_key": user},
        {"$set": {"allowed": True, "usage_count": 0, "expires_at": expiry}},
        upsert=True
    )
    return f"✅ User '{user}' added for {days} days"

@app.route("/ban")
def ban_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403

    users.update_one({"api_key": user}, {"$set": {"allowed": False}})
    return f"❌ User '{user}' banned"

@app.route("/unban")
def unban_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403

    users.update_one({"api_key": user}, {"$set": {"allowed": True}})
    return f"✅ User '{user}' unbanned"

@app.route("/stats")
def stats():
    secret = request.args.get("secret")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403

    all_users = list(users.find({}, {"_id": 0}))
    return {"users": all_users}

@app.route("/api")
def short_link():
    api_key = request.args.get("api")
    long_url = request.args.get("link")

    if not api_key or not long_url or "amazon." not in long_url:
        return "❌ Missing or invalid parameters", 400

    user = users.find_one({"api_key": api_key})
    if not user:
        return "❌ Invalid API key", 403
    if not user.get("allowed", False):
        return "❌ User is banned", 403
    if user.get("expires_at") and datetime.utcnow() > user["expires_at"]:
        return "❌ API key expired", 403

    encoded_url = urllib.parse.quote_plus(long_url)
    shortener_url = f"https://www.amazon.in/associates/sitestripe/getShortUrl?longUrl={encoded_url}&marketplaceId=44571"
    r = requests.get(shortener_url, headers=HEADERS)

    if r.status_code == 200:
        short_url = r.json().get("shortUrl")
        if short_url:
            users.update_one({"api_key": api_key}, {"$inc": {"usage_count": 1}})
            return short_url
        else:
            return "❌ Failed to shorten URL", 500
    else:
        return f"❌ Error {r.status_code}", r.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
