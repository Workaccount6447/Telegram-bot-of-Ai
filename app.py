from flask import Flask, request, jsonify
import requests
import time
import json

app = Flask(__name__)

ADMIN_PASSWORD = "ayusar@2010"
KVDB_BUCKET = "Rz199m1zbC8oEghG9br7Xx"

# Constants
KVDB_BASE = f"https://kvdb.io/{KVDB_BUCKET}"

COOKIES = {
    "session-id": "258-2488057-5180660",
    "i18n-prefs": "INR",
    "ubid-acbin": "261-4559508-6367401",
    "lc-acbin": "en_IN",
    "session-token": "kMYueRXHPOnLSoZbPU8gQGM+ZvH4o3kaUmmvAb6O3Sn9n7kf+Mbp15K7ME9/JeNyElnN15loNHbgrhFim2DX+TnAdBioWkCg95K3A2Z3z18WR2YWw/khe4YHPzh7xq49bxKnEpinxvJtomFlcmXK6w8luI9GJrANgdE+Jfz6fAXEHB9OaFCVZBREfZ4SmiqIFlu0euN8vJiiQvyN7MokLZtMCHgm0jgT/1bKvAg4T+dvC1UWdDgXnyyn3WDrWpJrNEMhw7VkWtQdtyBtqwZm8RW4zeBYXT0ACgQX3w2Gt+TDLfi1qMfzGrc7BrnoTog/IJP0aFl1UNm6r2Sv4/ezfuWuBKYmO0BIzgerV/iXtM/aNtDXKbzWvw==",
    "x-acbin": "DxeegW?GpvOj5BdJQr8fro?VHaJn0x1s38BwqvcdjnOeWcY1fcM1DR@YSTGDqeIv",
    "at-acbin": "Atza|IwEBIGrPdsKViIFV3vXk45oZyvSTJgXZwGgTDik1420XqGKf19SUvokB5kD8ZUQJJ3fPeRV2zBgIXbRsZ3mlPYcVEvqZRslymsXtIwr4aER9vxSA4C6ynoJoaOPvsSCefVslWCDjcYXOchzH_j72nupTxiyLyVE8Vuoc49VoXJzHzh0kyK8YPoh7MvqhaKEqANuuowpJpprxJ7X3CbDPlUSe0GK22mczsnJKotQgB886JcJ9bA",
    "sess-at-acbin": "J1itGQHJEtoSeLrRhPBFaCgs/eaBJjSFj+2ICVOImz4=",
    "sst-acbin": "Sst1|PQE0lr1Nm8snEKqclCaPO0Z0Ce7N1g8X2W0nk0KZ_6IRHbNnYFiN3dfKeZqfjtP47Fe1XOo_yUL3_lfvqgtmqXabSsO5jAzFQ5hHrjkk_KyFkXc2EceMqVpJcdgV209zWJYwoQ4P0p79fSdCg87ogsgDRsA2esUlWDI2ABdvZzZTincS5VRlusQXWfrsqubSloXR3iHzxhmYBu6QPHtWdQVGFmkecFZOT9kDvBY98ntTZMS04Oo1UluLNcQmxNfYSRn01OvUyG5-_Nj-e-XnB9WI-Zr8EuZxoKujQt8UPseGOo8",
    "session-id-time": "2082787201l",
    "rxc": "ALP/Gyk0bPxApKunGK4",
    "csm-hit": "tb:JXRQ8HRKDHCNJ9HGGRD0+s-JXRQ8HRKDHCNJ9HGGRD0|1755534447174&t:1755534447174&adb:adblk_no"
}
    

HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36"
}

# KVDB Helpers
def kv_set(key, value):
    requests.post(f"{KVDB_BASE}/{key}", data=json.dumps(value))

def kv_get(key, default=None):
    r = requests.get(f"{KVDB_BASE}/{key}")
    return json.loads(r.text) if r.status_code == 200 else default

@app.route("/")
def index():
    return "✅ Amazon Shortlink API is Live!"

@app.route("/adduser")
def add_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    days = int(request.args.get("days", 30))
    if secret != ADMIN_PASSWORD:
        return "❌ Invalid secret"
    users = kv_get("users", {})
    users[user] = {"added": int(time.time()), "expiry": int(time.time()) + days * 86400}
    kv_set("users", users)
    return f"✅ User '{user}' added for {days} days."

@app.route("/ban")
def ban_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != ADMIN_PASSWORD:
        return "❌ Invalid secret"
    banned = kv_get("banned", [])
    if user not in banned:
        banned.append(user)
        kv_set("banned", banned)
    return f"⛔ User '{user}' is banned."

@app.route("/unban")
def unban_user():
    secret = request.args.get("secret")
    user = request.args.get("user")
    if secret != ADMIN_PASSWORD:
        return "❌ Invalid secret"
    banned = kv_get("banned", [])
    if user in banned:
        banned.remove(user)
        kv_set("banned", banned)
    return f"✅ User '{user}' is unbanned."

@app.route("/stats")
def stats():
    secret = request.args.get("secret")
    if secret != ADMIN_PASSWORD:
        return "❌ Invalid secret"
    return jsonify(kv_get("stats", {}))

@app.route("/api")
def shorten():
    user = request.args.get("api")
    long_url = request.args.get("link")
    if not user or not long_url:
        return "❌ Missing user or link"

    users = kv_get("users", {})
    if user not in users:
        return "❌ Unauthorized user"

    if int(time.time()) > users[user]["expiry"]:
        return "❌ User expired"

    banned = kv_get("banned", [])
    if user in banned:
        return "⛔ User is banned"

    usage = kv_get("stats", {})
    usage[user] = usage.get(user, 0) + 1
    kv_set("stats", usage)

    params = {"longUrl": long_url, "marketplaceId": "44571"}
    response = requests.get(
        "https://www.amazon.in/associates/sitestripe/getShortUrl",
        headers=HEADERS, cookies=COOKIES, params=params
    )

    if response.status_code == 200:
        return response.json().get("shortUrl", "❌ Could not parse short URL")
    else:
        return f"❌ Failed with status code {response.status_code}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
