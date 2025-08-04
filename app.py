from flask import Flask, request, jsonify
import urllib.parse
import requests
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://telegrambot:ayusar@2010@cluster0.mongodb.net/?retryWrites=true&w=majority")
db = client['amazon_shortener']
users_col = db['users']

# SiteStripe cookies and headers
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

# Owner secret for admin actions
OWNER_SECRET = "ayusar@2010"

@app.route('/api')
def shorten_amazon_link():
    user_key = request.args.get('api')
    amazon_link = request.args.get('link')

    if not user_key or not amazon_link or "amazon." not in amazon_link:
        return "❌ Invalid parameters", 400

    user = users_col.find_one({"api_key": user_key})
    if not user:
        return "❌ Invalid API key", 403

    # Shorten Amazon link
    encoded = urllib.parse.quote_plus(amazon_link)
    shortener_url = f"https://www.amazon.in/associates/sitestripe/getShortUrl?longUrl={encoded}&marketplaceId=44571"
    r = requests.get(shortener_url, headers=HEADERS)

    if r.status_code == 200:
        short_url = r.json().get("shortUrl", None)
        if short_url:
            users_col.update_one(
                {"api_key": user_key},
                {"$inc": {"requests": 1}, "$set": {"last_used": datetime.utcnow()}}
            )
            return short_url
        return "❌ Failed to extract short URL", 500
    else:
        return f"❌ API error {r.status_code}", r.status_code

@app.route('/adduser')
def add_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != OWNER_SECRET or not user:
        return "❌ Unauthorized or missing user", 403

    users_col.update_one(
        {"api_key": user},
        {"$setOnInsert": {"requests": 0, "created": datetime.utcnow()}},
        upsert=True
    )
    return f"✅ API access granted to: {user}"

@app.route('/stats')
def stats():
    secret = request.args.get("secret")
    if secret != OWNER_SECRET:
        return "❌ Unauthorized", 403

    all_users = users_col.find()
    response = []
    for user in all_users:
        response.append({
            "api_key": user["api_key"],
            "requests": user.get("requests", 0),
            "last_used": user.get("last_used", "Never")
        })
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
