from flask import Flask, request
import requests
import urllib.parse
from pymongo import MongoClient
from datetime import datetime
from urllib.parse import quote_plus

# Flask app
app = Flask(__name__)

# MongoDB connection
username = quote_plus("telegrambot")
password = quote_plus("ayusar@2010")
mongo_uri = f"mongodb+srv://{username}:{password}@cluster0.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
db = client["amazon_shortener"]
users_col = db["users"]

# Working SiteStripe cookies
COOKIES = (
    "session-id=258-2488057-5180660; "
    "i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
    "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVji...; "
    'sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; '
    "sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7...; "
    "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndz...;"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": COOKIES
}

OWNER_PASSWORD = "ayusar@2010"

@app.route("/")
def index():
    return "✅ Amazon Shortener API is Live"

@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != OWNER_PASSWORD or not user:
        return "❌ Unauthorized or missing user", 403
    users_col.update_one(
        {"api_key": user},
        {"$set": {"allowed": True, "usage": 0, "created_at": datetime.utcnow()}},
        upsert=True
    )
    return f"✅ User '{user}' added successfully"

@app.route("/api")
def shorten_link():
    api = request.args.get("api")
    long_url = request.args.get("link")

    if not api or not long_url:
        return "❌ Missing parameters", 400

    user = users_col.find_one({"api_key": api, "allowed": True})
    if not user:
        return "❌ Invalid or unauthorized API key", 403

    if "amazon." not in long_url:
        return "❌ Invalid Amazon link", 400

    encoded = urllib.parse.quote_plus(long_url)
    url = f"https://www.amazon.in/associates/sitestripe/getShortUrl?longUrl={encoded}&marketplaceId=44571"
    r = requests.get(url, headers=HEADERS)

    if r.status_code == 200:
        short_url = r.json().get("shortUrl")
        users_col.update_one({"api_key": api}, {"$inc": {"usage": 1}})
        return short_url or "❌ Short URL not found"
    else:
        return f"❌ Error {r.status_code}", r.status_code

@app.route("/stats")
def get_stats():
    secret = request.args.get("secret")
    if secret != OWNER_PASSWORD:
        return "❌ Unauthorized", 403

    data = list(users_col.find({}, {"_id": 0}))
    return {"users": data}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
