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

    # ⏰ 30 minutes expiry
    if time.time() - data["time"] > 1800:
        return "<h2>❌ Link Expired</h2>"

    short = data["short"]

    # 1 sec animation then redirect
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta http-equiv="refresh" content="1;url={short}">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body {{
  margin:0;
  height:100vh;
  display:flex;
  justify-content:center;
  align-items:center;
  font-family:Arial, sans-serif;
  background:linear-gradient(135deg,#0b0f2a,#141a3a);
  color:white;
}}

.card {{
  width:90%;
  max-width:380px;
  padding:30px;
  border-radius:20px;
  background:rgba(255,255,255,0.05);
  backdrop-filter: blur(10px);
  box-shadow:0 0 25px rgba(0,0,0,0.4);
  text-align:center;
}}

.icon {{
  font-size:45px;
  margin-bottom:15px;
}}

.title {{
  font-size:26px;
  font-weight:bold;
}}

.sub {{
  opacity:0.7;
  margin-top:5px;
}}

.scan {{
  margin-top:25px;
  padding:15px;
  border-radius:15px;
  background:rgba(0,255,170,0.1);
  border:1px solid rgba(0,255,170,0.3);
  font-size:18px;
}}

.footer {{
  margin-top:20px;
  opacity:0.6;
  font-size:14px;
}}
</style>
</head>

<body>
  <div class="card">
      <div class="icon">🔒</div>
      <div class="title">Secure System</div>

      <div class="scan">
        ✔ Secure Like Bot verification complete
        <br>Scanning...
      </div>

      <div class="footer">Protected by Secure Redirect</div>
  </div>
</body>
</html>
"""

# Vercel handler
def handler(request, context):
    return app(request.environ, lambda *args: None)
