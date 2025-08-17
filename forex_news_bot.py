import os
import requests
import time
import schedule
import datetime
import telebot

# === CONFIG FROM ENV VARIABLES ===
BOT_TOKEN = "8318698327:AAHIUm8e3ty2mh8q-Crj7BoqIMyFlg7LcRk"
CHAT_ID = "-1002786950182"  
EMAIL = "natikuzmi@gmail.com"
PASSWORD = "2Y5drzMD@r@52X5"

bot = telebot.TeleBot(BOT_TOKEN)
MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "NZD", "CHF"]

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
    bot.send_message(CHAT_ID, msg.strip())

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
    except Exception as e:
        print("Error scheduling alerts:", e)

# === MAIN LOOP ===
schedule_alerts()
while True:
    schedule.run_pending()
    time.sleep(30)

