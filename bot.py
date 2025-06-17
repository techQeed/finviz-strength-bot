import os
from finvizfinance.forex import Forex
from telegram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler

# Load your secure credentials
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
chat_id = int(os.getenv("TELEGRAM_CHAT_ID"))

fx = Forex()
last_order = []

def get_order():
    df = fx.performance(change='percent')
    return df['Ticker'].tolist()

def check_strength():
    global last_order
    current = get_order()
    if last_order and current != last_order:
        bot.send_message(chat_id, "🔁 Ranking changed:\n" + " ".join(current))
    last_order = current

def scheduled_send():
    current = get_order()
    bot.send_message(chat_id, "🔔 Ranking update:\n" + " ".join(current))

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(check_strength, 'interval', minutes=10)
    scheduler.add_job(scheduled_send, 'cron', day_of_week='mon-fri', hour='0,1,2,3,4', minute=0)
    check_strength()  # initial check
    scheduler.start()
