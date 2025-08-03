from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# 🔐 Admin Secret
ADMIN_SECRET = "ayusar@2010"

# 🍪 Session Cookie & Headers
COOKIE = """session-id=258-2488057-5180660; i18n-prefs=INR; lc-acbin=en_IN; ubid-acbin=261-4559508-6367401; at-acbin=Atza|IwEBIEbJvF6zMWwxVJcwM1cBBLghJa0IfhJpu6guwxQJVjiDQa_k6d-nTd1ewlINt1H717wsqcqhDsLfxZxMcOM26emvQ7eyM0EL0xjPfmPE6S4M3AImz7lEPXzp9OLOEhsASbBF9tLwmBsh9BZN1iW6eS8Mcg3BOAPFJ_hgIReqCW2w76NcI-YHZMF1iCRUV93S1zYKNPEV7uOWSKm6lFA-pwCpXSq7eyuvVIGXV8OydRSO3if46hr0RbZ0OCVZIQd5yUYnO1BR3wcoKiadvX0Te_eJ9l2dYcvEH1f6eShaietZUQ; sess-at-acbin="h+U5YvpWslcHY6OcLVwtxT4rDLhKz7Xk98Y4GvGZtXc="; sst-acbin=Sst1|PQFv1S46auCLoPSSrLhkPOtTCdR9ElFfR_jOzLlcc1qPpo7d4skHpI37UUs9hYJdUYvVhP2x8cSCBQ_JNnsSDobBdHXdErkDcdETcuEVbPdsa8AGWZopvv4KteadwAJBsRJ8TmcX6xQYaWROTsYv6VXUi3dAE_0nlVP1wMgWJrU8sX-8N98dee741VPb33OryrsdjSlUPOAzChZUblgGlZigMCjv-d8P3uDp1mmSBYpkQiRlLfCFEYJQVVIka6jrAQhjpgm1mGecd30s01IgKVUWl8BH94rcgS6sEJipsOQ82KY; session-id-time=2082787201l; session-token=92JP3YPrXa2aM7UC3MVeNEU2hwg0UUC0SMwey9/Rfj6zndzFtanm37h2rHWcB17jbLwYIdikWnh7ROHLvi2BZ0kUXu1Z2OA3weWO5yRkKCPvuDyWisI0QGuUxw8deMQGaz4kEI8/0u+GGTx30WeLY7kdIpMpCZxcaOSOnK2z5JEs9ILcgb+XywdyYHrJje0NpqXR9ux1IyOiULtA8UdFmT7LIDcnBYXiK1DLcK49CjmJqK8gGTRDgwdt96qBiNoObLj06ELkTCt66B83rTEy2MrlXsgpv4/DPthRMojSPfeHrrchldTliToqvp2ui3lF3IZucSVYZTuf2fvjIxBOqHCuAqAv9lD1xvNyPA3llI8rte8iAry4oGnNHqtVDytF; x-acbin="jNnyveSVr43Beaxh@GIWqPT@DuKtCJbTBAn?tLN0k7Rj3v5YWtB1U@?XUro8Xzsv"; rxc=ABPYjmcKVz3v13CWRkY"""
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "cookie": COOKIE
}

# 📂 File paths
USER_FILE = "users.json"
BAN_FILE = "banned.json"
USAGE_FILE = "usage.json"

def load_json(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump(default, f)
    with open(file) as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f)

# ✅ Add user (API allowed)
@app.route("/adduser")
def add_user():
    if request.args.get("secret") != ADMIN_SECRET:
        return "❌ Invalid admin secret", 403
    user = request.args.get("user")
    if not user:
        return "❌ Missing user", 400
    users = load_json(USER_FILE, [])
    if user not in users:
        users.append(user)
        save_json(USER_FILE, users)
    return f"✅ API user `{user}` added."

# ⛔ Ban user
@app.route("/ban")
def ban_user():
    if request.args.get("secret") != ADMIN_SECRET:
        return "❌ Invalid admin secret", 403
    user = request.args.get("user")
    if not user:
        return "❌ Missing user", 400
    banned = load_json(BAN_FILE, [])
    if user not in banned:
        banned.append(user)
        save_json(BAN_FILE, banned)
    return f"🚫 API user `{user}` banned."

# ✅ Unban user
@app.route("/unban")
def unban_user():
    if request.args.get("secret") != ADMIN_SECRET:
        return "❌ Invalid admin secret", 403
    user = request.args.get("user")
    if not user:
        return "❌ Missing user", 400
    banned = load_json(BAN_FILE, [])
    if user in banned:
        banned.remove(user)
        save_json(BAN_FILE, banned)
    return f"✅ API user `{user}` unbanned."

# 📊 Stats
@app.route("/stats")
def stats():
    if request.args.get("secret") != ADMIN_SECRET:
        return "❌ Invalid admin secret", 403
    return jsonify(load_json(USAGE_FILE, {}))

# 🔗 API usage
@app.route("/api")
def api():
    user = request.args.get("api")
    link = request.args.get("link")

    if not user or not link:
        return "❌ Missing api or link", 400

    users = load_json(USER_FILE, [])
    banned = load_json(BAN_FILE, [])
    usage = load_json(USAGE_FILE, {})

    if user not in users:
        return "❌ API user not registered", 403
    if user in banned:
        return "❌ API access is banned", 403

    response = requests.get(
        "https://www.amazon.in/associates/sitestripe/getShortUrl",
        headers=HEADERS,
        params={"longUrl": link, "marketplaceId": "44571"}
    )

    if response.status_code == 200:
        data = response.json()
        short_url = data.get("shortUrl")
        if short_url:
            usage[user] = usage.get(user, 0) + 1
            save_json(USAGE_FILE, usage)
            return short_url
        return "❌ Short URL not found"
    return f"❌ Failed: {response.status_code}"

# 🟢 Home page
@app.route("/")
def home():
    return "✅ Amazon Link Shortener is Running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
