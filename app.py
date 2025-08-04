from flask import Flask, request, jsonify
import requests
import urllib.parse
import datetime
from supabase import create_client, Client

app = Flask(__name__)

# ✅ Amazon SiteStripe Cookies & Headers (paste your values here)
COOKIES = (
    "session-id=258-2488057-5180660; "
    "i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
    "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d-...; "
    'sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; '
    "sst-acbin=Sst1|...; "
    "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/...;"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": COOKIES
}

# ✅ Supabase setup
SUPABASE_URL = "https://qvmnnwilzcqmqroqpgll.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF2bW5ud2lsemNxbXFyb3FwZ2xsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQyMzMzMjYsImV4cCI6MjA2OTgwOTMyNn0.05XPEDCX1xsn_qa92joHMSbLQPlXkoW-Dwi79KGJG_k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

OWNER_SECRET = "ayusar@2010"

# ✅ Main API route
@app.route("/api")
def shorten_amazon_link():
    user = request.args.get("api")
    long_url = request.args.get("link")

    if not user or not long_url:
        return "❌ Missing api or link", 400

    if "amazon." not in long_url:
        return "❌ Invalid Amazon link", 400

    # Check if user is allowed
    user_data = supabase.table("users").select("*").eq("api_key", user).execute().data
    if not user_data:
        return "❌ Invalid API key", 403
    if not user_data[0]["allowed"]:
        return "❌ Access denied", 403

    # Shorten link
    encoded = urllib.parse.quote_plus(long_url)
    shortener_url = f"https://www.amazon.in/associates/sitestripe/getShortUrl?longUrl={encoded}&marketplaceId=44571"
    r = requests.get(shortener_url, headers=HEADERS)

    if r.status_code == 200:
        short_url = r.json().get("shortUrl")
        # Update usage count
        supabase.table("users").update({"usage_count": user_data[0]["usage_count"] + 1}).eq("api_key", user).execute()
        return short_url or "❌ Could not extract short URL"
    else:
        return f"❌ Error {r.status_code}", r.status_code

# ✅ Admin commands
@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != OWNER_SECRET:
        return "❌ Unauthorized", 403
    if not user:
        return "❌ Missing user", 400
    supabase.table("users").upsert({"api_key": user, "allowed": True, "usage_count": 0}).execute()
    return f"✅ User {user} added"

@app.route("/banuser")
def ban_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != OWNER_SECRET:
        return "❌ Unauthorized", 403
    supabase.table("users").update({"allowed": False}).eq("api_key", user).execute()
    return f"❌ User {user} banned"

@app.route("/unbanuser")
def unban_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != OWNER_SECRET:
        return "❌ Unauthorized", 403
    supabase.table("users").update({"allowed": True}).eq("api_key", user).execute()
    return f"✅ User {user} unbanned"

@app.route("/stats")
def stats():
    secret = request.args.get("secret")
    if secret != OWNER_SECRET:
        return "❌ Unauthorized", 403
    data = supabase.table("users").select("*").execute().data
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
    
