from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
import urllib.parse
import requests

# MongoDB connection
mongo_uri = "mongodb+srv://telegrambot:ayusar%402010@cluster0.kdocaah.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = client["amazonshort"]
users_col = db["users"]

# Amazon SiteStripe Cookie (Already provided by you)
COOKIES = (
    "session-id=258-2488057-5180660; "
    "i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
    "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d-...; "
    'sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; '
    "sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7d4sk...; "
    "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndzFtanm3...;"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": COOKIES
}

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Amazon Shortener API is Live!"

@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403

    user = request.args.get("user")
    days = int(request.args.get("days", 99999))
    if not user:
        return "❌ Missing user param", 400

    expiry = datetime.utcnow() + timedelta(days=days)
    users_col.update_one(
        {"api_key": user},
        {"$set": {"allowed": True, "usage_count": 0, "expiry": expiry}},
        upsert=True
    )
    return f"✅ User `{user}` added with expiry of {days} days."

@app.route("/ban")
def ban_user():
    secret = request.args.get("secret")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403
    user = request.args.get("user")
    if not user:
        return "❌ Missing user", 400
    users_col.update_one({"api_key": user}, {"$set": {"allowed": False}})
    return f"❌ User `{user}` has been banned."

@app.route("/unban")
def unban_user():
    secret = request.args.get("secret")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403
    user = request.args.get("user")
    if not user:
        return "❌ Missing user", 400
    users_col.update_one({"api_key": user}, {"$set": {"allowed": True}})
    return f"✅ User `{user}` has been unbanned."

@app.route("/api")
def shorten_amazon_link():
    api_key = request.args.get("api")
    link = request.args.get("link")

    if not api_key or not link:
        return "❌ Missing 'api' or 'link'", 400

    user = users_col.find_one({"api_key": api_key})
    if not user:
        return "❌ API Key not found", 403
    if not user.get("allowed", False):
        return "❌ Access Denied", 403
    if "expiry" in user and datetime.utcnow() > user["expiry"]:
        return "❌ API expired", 403

    encoded_url = urllib.parse.quote_plus(link)
    shortener_url = f"https://www.amazon.in/associates/sitestripe/getShortUrl?longUrl={encoded_url}&marketplaceId=44571"

    try:
        r = requests.get(shortener_url, headers=HEADERS)
        r.raise_for_status()
        data = r.json()
        users_col.update_one({"api_key": api_key}, {"$inc": {"usage_count": 1}})
        return data.get("shortUrl", "❌ Failed to shorten")
    except Exception as e:
        return f"❌ Error: {str(e)}", 500

@app.route("/stats")
def view_stats():
    secret = request.args.get("secret")
    if secret != "ayusar@2010":
        return "❌ Unauthorized", 403

    users = list(users_col.find({}, {"_id": 0}))
    return jsonify(users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
