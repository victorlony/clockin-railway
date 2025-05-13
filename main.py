import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

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
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

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

    if telegram_token and telegram_chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                data={"chat_id": telegram_chat_id, "text": message}
            )
        except:
            pass

    return message

# 🔐 密碼保護用 token
UPDATE_AUTH_TOKEN = "chy2025"

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
        <a href="https://pro.104.com.tw/psc2" target="_blank">
            👉 開啟 104 登入頁
        </a>
        <br><br>
        <form action="/grab-cookie" method="POST">
            <button type="submit">✅ 我已登入，抓取 cookie</button>
        </form>
    </body>
    </html>
    """)

@app.route("/grab-cookie", methods=["POST"])
def grab_cookie():
    # ❗ TODO：未來這裡可以串真實 Selenium 自動登入並取得 cookie
    msg = "✅ Cookie 模擬更新完成！（實作版可串 Railway API 更新變數）"

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if telegram_token and telegram_chat_id:
        try:
            requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                data={"chat_id": telegram_chat_id, "text": msg}
            )
        except:
            pass

    return msg

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
