from flask import Flask, request, jsonify
import requests
from supabase import create_client, Client

app = Flask(__name__)

# Admin secret key
ADMIN_SECRET = "ayusar@2010"

# Supabase credentials
SUPABASE_URL = "https://qvmnnwilzcqmqroqpgll.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF2bW5ud2lsemNxbXFyb3FwZ2xsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQyMzMzMjYsImV4cCI6MjA2OTgwOTMyNn0.05XPEDCX1xsn_qa92joHMSbLQPlXkoW-Dwi79KGJG_k"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 🔒 Amazon Cookie (Full version — exactly as you provided)
COOKIE = (
    "session-id=258-2488057-5180660; i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
    "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d-nTd1ewlINt1H717wsqcqhDsLfxZxMcOM26emvQ7eyM0EL0xjPfmPE6S4M3AImz7lEPXzp9OLOEhsASbBF9tLwmBsh9BZN1iW6eS8Mcg3BOAPFJ_hgIReqCW2w76NcI-YHZMF1iCRUV93S1zYKNPEV7uOWSKm6lFA-pwCpXSq7eyuvVIGXV8OydRSO3if46hr0RbZ0OCVZIQd5yUYnO1BR3wcoKiadvX0Te_eJ9l2dYcvEH1f6eShaietZUQ; "
    "sess-at-acbin=\"h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc=\"; "
    "sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7d4skHpI37UUs9hYJdUYvVhP2x8cSCBQ_JNnsSDobBdHXdErkDcdETcuEVbPdsa8AGWZopvv4KteadwAJBsRJ8TmcX6xQYaWROTsYv6VXUi3dAE_0nlVP1wMgWJrU8sX-8N98dee741VPb33OryrsdjSlUPOAzChZUblgGlZigMCjv-d8P3uDp1mmSBYpkQiRlLfCFEYJQVVIka6jrAQhjpgm1mGecd30s01IgKVUWl8BH94rcgS6sEJipsOQ82KY; "
    "session-id-time=2082787201l; "
    "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndzFtanm37h2rHWcB17jbLwYIdikWnh7ROHLvi2BZ0kUXu1Z2OA3weWO5yRkKCPvuDyWisI0QGuUxw8deMQGaz4kEI8/0u+GGTx30WeLY7kdIpMpCZxcaOSOnK2z5JEs9ILcgb+XywdyYHrJje0NpqXR9ux1IyOiULtA8UdFmT7LIDcnBYXiK1DLcK49CjmJqK8gGTRDgwdt96qBiNoObLj06ELkTCt66B83rTEy2MrlXsgpv4/DPthRMojSPfeHrrchldTliToqvp2ui3lF3IZucSVYZTuf2fvjIxBOqHCuAqAv9lD1xvNyPA3llI8rte8iAry4oGnNHqtVDytF; "
    "x-acbin=\"jNnyveSVr43Beaxh@GIWqPT@DuKtCJbTBAn?tLN0k7Rj3v5YWtB1U@?XUro8Xzsv\"; "
    "rxc=ABPYjmcKVz3v13CWRkY"
)

HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "cookie": COOKIE
}

@app.route("/")
def home():
    return "✅ Amazon Shortener API with Supabase is running!"

@app.route("/api")
def shorten():
    user = request.args.get("api")
    link = request.args.get("link")

    if not user or not link:
        return "❌ Missing api or link", 400

    # Check user
    check_user = supabase.table("users").select("*").eq("username", user).execute()
    if not check_user.data:
        return "❌ Unauthorized user", 403

    # Check if banned
    banned = supabase.table("banned_users").select("*").eq("username", user).execute()
    if banned.data:
        return "🚫 You are banned from API", 403

    # Call Amazon Shortener API
    res = requests.get(
        "https://www.amazon.in/associates/sitestripe/getShortUrl",
        headers=HEADERS,
        params={"longUrl": link, "marketplaceId": "44571"}
    )

    if res.status_code == 200 and res.json().get("shortUrl"):
        short_url = res.json()["shortUrl"]
        # update usage
        usage = supabase.table("usage_stats").select("*").eq("username", user).execute()
        if usage.data:
            count = usage.data[0]["count"]
            supabase.table("usage_stats").update({"count": count + 1}).eq("username", user).execute()
        else:
            supabase.table("usage_stats").insert({"username": user, "count": 1}).execute()
        return short_url

    return "❌ Amazon shortening failed"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
    
