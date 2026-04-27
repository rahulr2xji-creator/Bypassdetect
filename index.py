from flask import Flask, request
import requests, time, string, random

app = Flask(__name__)

AROLINK_API = "82288e6f415eb47c5e596a29d2f1df044ed42620"
DOMAIN = "https://bypassdetect-one.vercel.app"

DB = {}

# random id generator
def gen_id():
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(6))

# ===============================
# BOT CALL API
# ===============================
@app.route("/generate")
def generate():
    url = request.args.get("url")

    if not url:
        return "url missing"

    # 🔗 short with arolinks
    api = f"https://arolinks.com/api?api={AROLINK_API}&url={url}&format=text"
    short_link = requests.get(api).text

    gid = gen_id()

    DB[gid] = {
        "short": short_link,
        "time": time.time()
    }

    # return gateway link
    return f"{DOMAIN}/{gid}"


# ===============================
# GATEWAY REDIRECT PAGE
# ===============================
@app.route("/<gid>")
def open_link(gid):

    if gid not in DB:
        return "<h2>Invalid Link</h2>"

    data = DB[gid]

    # ⏰ 30 min expiry
    if time.time() - data["time"] > 1800:
        return "<h2>❌ Link Expired</h2>"

    short = data["short"]

    return f"""
<!DOCTYPE html>
<html>
<head>

<!-- ⚡ instant redirect -->
<script>
window.location.replace("{short}");
</script>

<!-- ⚡ backup redirect -->
<meta http-equiv="refresh" content="0;url={short}">

</head>

<body style="background:#111;color:white;text-align:center;padding-top:50px;">
<h3>🔗 Opening Link...</h3>

<script>
window.location.href = "{short}";
</script>

</body>
</html>
"""

# Vercel handler
def handler(request, context):
    return app(request.environ, lambda *args: None)
