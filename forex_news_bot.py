# forex_news_bot.py
import os
import requests
import time
import datetime
import schedule
import threading
import telebot
from flask import Flask

import time

# Wait 5–10 seconds before sending startup message
time.sleep(10)
try:
    bot.send_message(CHAT_ID, "✅ Telegram bot is running and connected to this group!")
except Exception as e:
    print("Failed to send startup message:", e)

# === CONFIG FROM ENV VARIABLES ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = int(os.environ.get("CHAT_ID"))
EMAIL = os.environ.get("EMAIL")
PASSWORD = os.environ.get("PASSWORD")

bot = telebot.TeleBot(BOT_TOKEN)
MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "NZD", "CHF"]

# === FLASK SERVER TO KEEP RENDER ALIVE ===
app = Flask(__name__)

@app.route("/")
def index():
    return "Forex News Bot is running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# === MYFXBOOK API FUNCTIONS ===
def login():
    url = f"https://www.myfxbook.com/api/login.json?email={EMAIL}&password={PASSWORD}"
    r = requests.get(url, proxies={"http": None, "https": None}).json()
    if r["error"]:
        raise Exception("Login failed: " + r["message"])
    return r["session"]

def fetch_calendar(session):
    url = f"https://www.myfxbook.com/api/get-economic-calendar.json?session={session}"
    r = requests.get(url, proxies={"http": None, "https": None}).json()
    if r["error"]:
        raise Exception("Calendar fetch failed: " + r["message"])
    return r["calendar"]

# === ALERT FUNCTION ===
def send_alert(event, minutes_before):
    msg = f"""
⚠️ RED FOLDER NEWS ALERT ⚠️
Currency: {event['country']}
Event: {event['title']}
Impact: {event['impact']}
Time: {event['date']}
⏰ Starts in {minutes_before} minutes
"""
    try:
        bot.send_message(CHAT_ID, msg.strip())
    except Exception as e:
        print("Failed to send alert:", e)

# === HEARTBEAT FUNCTION ===
def heartbeat():
    try:
        bot.send_message(CHAT_ID, "💓 Bot is alive and running!")
    except Exception as e:
        print("Failed to send heartbeat:", e)

# Schedule heartbeat every 3 hours
schedule.every(3).hours.do(heartbeat)

# === SCHEDULE ALERTS ===
def schedule_alerts():
    try:
        session = login()
        events = fetch_calendar(session)
        now = datetime.datetime.utcnow()

        for event in events:
            if event["impact"] == "High" and event["country"] in MAJOR_CURRENCIES:
                event_time = datetime.datetime.strptime(event["date"], "%Y-%m-%d %H:%M:%S")
                for minutes_before in [60, 30, 15, 5]:
                    alert_time = event_time - datetime.timedelta(minutes=minutes_before)
                    if alert_time > now:
                        schedule.every().day.at(alert_time.strftime("%H:%M")).do(
                            send_alert, event=event, minutes_before=minutes_before
                        )
                        print(f"Scheduled: {event['title']} ({event['country']}) {minutes_before}m before")
        # Send test message on startup
        bot.send_message(CHAT_ID, "✅ Telegram bot is running and connected to this group!")
    except Exception as e:
        print("Error scheduling alerts:", e)

schedule_alerts()

# === MAIN LOOP ===
while True:
    schedule.run_pending()
    time.sleep(30)




