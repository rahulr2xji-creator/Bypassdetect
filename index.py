from flask import Flask, request, jsonify
from nanoid import generate
import time

app = Flask(__name__)

TOKENS = {}

# -----------------------------
# LINK GENERATE API
# -----------------------------
@app.route("/create")
def create():
    user = request.args.get("user")

    if not user:
        return jsonify({"error":"user missing"}),400

    token = generate(size=10)

    TOKENS[token] = {
        "user": user,
        "time": time.time(),
        "used": False
    }

    gate_link = f"https://bypassdetect-one.vercel.app/gate?token={token}"

    return jsonify({"link": gate_link})


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
    <meta http-equiv="refresh" content="6;url=/verify?token={token}">
    </head>

    <body style="text-align:center;padding-top:50px;font-family:sans-serif;">
    <h2>🔐 Verifying human...</h2>
    <p>Please wait 5 seconds</p>

    <script>
    document.cookie = "human=1; max-age=60";
    </script>
    </body>
    </html>
    """

    return html


# -----------------------------
# VERIFY PAGE (CREDIT)
# -----------------------------
@app.route("/verify")
def verify():
    token = request.args.get("token")

    if token not in TOKENS:
        return "Invalid"

    data = TOKENS[token]

    if data["used"]:
        return "Already used"

    if time.time() - data["time"] < 5:
        return "Bypass detected"

    if "human=1" not in request.headers.get("Cookie",""):
        return "Bypass blocked"

    ua = request.headers.get("User-Agent","")
    if "Mozilla" not in ua:
        return "Bot blocked"

    TOKENS[token]["used"] = True

    return "🎉 Credit Added Successfully"


# Vercel handler
def handler(request, context):
    return app(request.environ, lambda *args: None)
