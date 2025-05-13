import os
import requests
from flask import Flask

app = Flask(__name__)

@app.route("/clockin", methods=["GET"])
def clockin():
    try:
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

        res = requests.post("https://pro.104.com.tw/psc2/api/f0400/newClockin", headers=headers)

        if res.status_code == 200:
            message = "✅ [104] 打卡成功！"
        else:
            message = f"❌ 打卡失敗：{res.status_code}"

        if telegram_token and telegram_chat_id:
            requests.post(
                f"https://api.telegram.org/bot{telegram_token}/sendMessage",
                data={"chat_id": telegram_chat_id, "text": message}
            )

        return message

    except Exception as e:
        return f"⚠️ 發生錯誤：{e}"

@app.route("/", methods=["GET"])
def home():
    return "✅ 104 自動打卡服務運作中"