import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

RAILWAY_API_TOKEN = "ed8e9b45-9e51-4d4f-8c7c-9f41235b7509"
PROJECT_ID = os.getenv("RAILWAY_PROJECT_ID")
SERVICE_ID = os.getenv("RAILWAY_SERVICE_ID")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
UPDATE_AUTH_TOKEN = "chy2025"


@app.route("/")
def home():
    return "✅ 104 自動打卡服務運作中"


@app.route("/clockin", methods=["GET", "POST"])
def clockin():
    if request.method == "POST":
        data = request.get_json()
        if not data or data.get("message", {}).get("text") != "/clockin":
            return "ignored", 200

    cookie = os.getenv("COOKIES")

    headers = {
        "Content-Type": "application/json",
        "Cookie": cookie,
        "Origin": "https://pro.104.com.tw",
        "Referer": "https://pro.104.com.tw/psc2",
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        res = requests.post("https://pro.104.com.tw/psc2/api/f0400/newClockin", headers=headers)
        if res.status_code == 200:
            message = "✅ [104] 打卡成功！"
        else:
            message = f"❌ 打卡失敗：{res.status_code}"
    except Exception as e:
        message = f"⚠️ 發生錯誤：{e}"

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
            )
        except:
            pass

    return message


@app.route("/update-cookie", methods=["GET"])
def update_cookie_page():
    if request.args.get("auth") != UPDATE_AUTH_TOKEN:
        return "🔒 Unauthorized", 403

    return render_template_string("""
    <html>
    <head><title>更新 104 Cookie</title></head>
    <body style="font-family: sans-serif;">
        <h2>🔐 104 Cookie 雲端更新工具</h2>
        <p>請先點選下方按鈕登入 104</p>
        <a href="https://pro.104.com.tw/psc2" target="_blank">👉 開啟 104 登入頁</a>
        <br><br>
        <form action="/grab-cookie" method="POST">
            <label>請貼上登入後的 Cookie：</label><br>
            <textarea name="cookie" rows="5" cols="80" required></textarea><br><br>
            <button type="submit">✅ 更新 Cookie 並通知 Telegram</button>
        </form>
    </body>
    </html>
    """)


@app.route("/grab-cookie", methods=["POST"])
def grab_cookie():
    cookie = request.form.get("cookie", "").strip()
    if not cookie:
        return "❌ Cookie 為空", 400

    message = "✅ Cookie 已更新至 Railway"

    # 呼叫 Railway API 更新變數
    url = f"https://backboard.railway.app/project/{PROJECT_ID}/service/{SERVICE_ID}/variables"
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {"updates": [{"key": "COOKIES", "value": cookie}]}

    try:
        res = requests.patch(url, json=body, headers=headers)
        if res.status_code != 200:
            message = f"❌ 更新 Railway 失敗：{res.status_code} - {res.text}"
    except Exception as e:
        message = f"❌ 發生錯誤：{e}"

    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        try:
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
            )
        except:
            pass

    return message


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
