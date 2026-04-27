from flask import Flask, request, jsonify
from nanoid import generate
import time, requests

app = Flask(__name__)
TOKENS = {}

AROLINK_API = "82288e6f415eb47c5e596a29d2f1df044ed42620"
DOMAIN = "https://bypassdetect-one.vercel.app"

# -----------------------------
# CREATE SHORT LINK API
# -----------------------------
@app.route("/create")
def create():
    user = request.args.get("user")

    if not user:
        return jsonify({"error":"user missing"}),400

    # 1️⃣ create token
    token = generate(size=12)

    TOKENS[token] = {
        "user": user,
        "time": time.time(),
        "used": False
    }

    # 2️⃣ real destination (gate link)
    gate_link = f"{DOMAIN}/gate?token={token}"

    # 3️⃣ call arolinks api
    short_api = (
        f"https://arolinks.com/api?"
        f"api={AROLINK_API}&url={gate_link}&format=text"
    )

    try:
        short_url = requests.get(short_api).text
    except:
        return "Shortener error"

    # 4️⃣ return short link
    return jsonify({"short_link": short_url})


# -----------------------------
# GATE PAGE (ANTI BYPASS)
# -----------------------------
@app.route("/gate")
def gate():
    token = request.args.get("token")

    if token not in TOKENS:
        return "Invalid link"

    html = f"""
    <html>
    <head>
    <meta http-equiv="refresh" content="7;url=/verify?token={token}">
    </head>

    <body style="text-align:center;padding-top:50px;font-family:sans-serif;">
    <h2>🔐 Verifying human...</h2>
    <p>Please wait 6 seconds</p>

    <script>
    document.cookie = "human=1; max-age=60";
    </script>
    </body>
    </html>
    """

    return html


# -----------------------------
# VERIFY PAGE (FINAL CREDIT)
# -----------------------------
@app.route("/verify")
def verify():
    token = request.args.get("token")

    if token not in TOKENS:
        return "Invalid"

    data = TOKENS[token]

    if data["used"]:
        return "Already used"

    # ⏱ bypass detection
    if time.time() - data["time"] < 6:
        return "Bypass detected"

    # 🍪 cookie check
    if "human=1" not in request.headers.get("Cookie",""):
        return "Bypass blocked"

    # 🤖 bot detection
    ua = request.headers.get("User-Agent","")
    if "Mozilla" not in ua:
        return "Bot blocked"

    TOKENS[token]["used"] = True

    return "🎉 Credit Added Successfully"


# Vercel handler
def handler(request, context):
    return app(request.environ, lambda *args: None)
