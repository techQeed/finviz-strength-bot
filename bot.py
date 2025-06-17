import os
import time
import requests
import telegram
from bs4 import BeautifulSoup
from datetime import datetime
import schedule

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = int(os.getenv("USER_ID"))
bot = telegram.Bot(token=BOT_TOKEN)

prev_order = []

def fetch_currency_order():
    url = "https://finviz.com/forex.ashx"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="t-full")
    rows = table.find_all("tr")[1:9]  # Get only the 8 currency rows

    currency_data = []
    for row in rows:
        columns = row.find_all("td")
        symbol = columns[0].text.strip()
        perf = float(columns[1].text.strip().replace("%", ""))
        currency_data.append((symbol, perf))

    sorted_data = sorted(currency_data, key=lambda x: x[1], reverse=True)
    ordered = [symbol for symbol, _ in sorted_data]
    return ordered

def check_and_alert():
    global prev_order
    current_order = fetch_currency_order()
    if prev_order and current_order != prev_order:
        msg = f"⚠️ Currency order changed:\n\nPrevious: {' '.join(prev_order)}\nNow:      {' '.join(current_order)}"
        bot.send_message(chat_id=USER_ID, text=msg)
    prev_order = current_order

def send_hourly_update():
    now = datetime.now()
    weekday = now.weekday()  # Monday is 0, Sunday is 6
    if weekday < 5:  # Only on weekdays
        current_order = fetch_currency_order()
        msg = f"🕒 Hourly Currency Strength (UTC {now.strftime('%H:%M')}):\n\n{' '.join(current_order)}"
        bot.send_message(chat_id=USER_ID, text=msg)

# Schedule the tasks
schedule.every(10).minutes.do(check_and_alert)

# Hourly Finviz order updates (weekdays only)
for hour in range(0, 5):
    schedule.every().day.at(f"{hour:02d}:00").do(send_hourly_update)

# Main loop
while True:
    schedule.run_pending()
    time.sleep(5)
