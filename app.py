from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔐 Admin password
ADMIN_SECRET = "ayusar@2010"

# ✅ API users with usage tracking (stored in memory)
USERS = {
    "Amazonpublicpaidbotforpersonaluse2010": {"usage": 0},
    "Dealsduniya": {"usage": 0}
}

# ✅ Your Amazon SiteStripe request headers (REPLACE values below with valid cookies/token!)
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "cookie": (
        "session-id=258-2488057-5180660; "
        "i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; "
        "at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d-nTd1ewlINt1H717wsqcqhDsLfxZxMcOM26emvQ7eyM0EL0xjPfmPE6S4M3AImz7lEPXzp9OLOEhsASbBF9tLwmBsh9BZN1iW6eS8Mcg3BOAPFJ_hgIReqCW2w76NcI-YHZMF1iCRUV93S1zYKNPEV7uOWSKm6lFA-pwCpXSq7eyuvVIGXV8OydRSO3if46hr0RbZ0OCVZIQd5yUYnO1BR3wcoKiadvX0Te_eJ9l2dYcvEH1f6eShaietZUQ; "
        'sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; '
        "sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7d4skHpI37UUs9hYJdUYvVhP2x8cSCBQ_JNnsSDobBdHXdErkDcdETcuEVbPdsa8AGWZopvv4KteadwAJBsRJ8TmcX6xQYaWROTsYv6VXUi3dAE_0nlVP1wMgWJrU8sX-8N98dee741VPb33OryrsdjSlUPOAzChZUblgGlZigMCjv-d8P3uDp1mmSBYpkQiRlLfCFEYJQVVIka6jrAQhjpgm1mGecd30s01IgKVUWl8BH94rcgS6sEJipsOQ82KY; "
        "session-id-time=2082787201l; "
        "session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndzFtanm37h2rHWcB17jbLwYIdikWnh7ROHLvi2BZ0kUXu1Z2OA3weWO5yRkKCPvuDyWisI0QGuUxw8deMQGaz4kEI8/0u+GGTx30WeLY7kdIpMpCZxcaOSOnK2z5JEs9ILcgb+XywdyYHrJje0NpqXR9ux1IyOiULtA8UdFmT7LIDcnBYXiK1DLcK49CjmJqK8gGTRDgwdt96qBiNoObLj06ELkTCt66B83rTEy2MrlXsgpv4/DPthRMojSPfeHrrchldTliToqvp2ui3lF3IZucSVYZTuf2fvjIxBOqHCuAqAv9lD1xvNyPA3llI8rte8iAry4oGnNHqtVDytF; "
        'x-acbin="jNnyveSVr43Beaxh@GIWqPT@DuKtCJbTBAn?tLN0k7Rj3v5YWtB1U@?XUro8Xzsv"; '
        "rxc=ABPYjmcKVz3v13CWRkY"
    )
}

@app.route("/api")
def shorten_amazon():
    apikey = request.args.get("api")
    long_url = request.args.get("link")

    if not apikey or apikey not in USERS:
        return jsonify({"error": "❌ Invalid API key"}), 403

    if not long_url or "amazon" not in long_url:
        return jsonify({"error": "❌ Missing or invalid Amazon link"}), 400

    params = {
        "longUrl": long_url,
        "marketplaceId": "44571"
    }

    res = requests.get("https://www.amazon.in/associates/sitestripe/getShortUrl", headers=HEADERS, params=params)

    if res.status_code == 200 and res.json().get("shortUrl"):
        USERS[apikey]["usage"] += 1
        return res.json()["shortUrl"]
    else:
        return f"❌ Amazon Error: {res.status_code}"

@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    new_user = request.args.get("user")

    if secret != ADMIN_SECRET:
        return "❌ Unauthorized"

    if not new_user:
        return "❌ Provide ?user=... in URL"

    if new_user in USERS:
        return f"⚠️ User '{new_user}' already exists."

    USERS[new_user] = {"usage": 0}
    return f"✅ User '{new_user}' added successfully!"

@app.route("/stats")
def usage_stats():
    secret = request.args.get("secret")
    if secret != ADMIN_SECRET:
        return "❌ Unauthorized to view usage."
    return jsonify(USERS)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
