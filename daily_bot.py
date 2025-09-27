import os
import requests
import datetime
import schedule
import time
import threading
from flask import Flask

# ====== Environment Variables ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
CRYPTO_NEWS_API_KEY = os.getenv("CRYPTO_NEWS_API_KEY")
FNO_DATA_API_KEY = os.getenv("FNO_DATA_API_KEY")

# ====== Flask App (for Render) ======
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Bot is running on Render!"

# ====== Fetch Stock News ======
def fetch_stock_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey={NEWS_API_KEY}"
    resp = requests.get(url).json()
    return resp.get("articles", [])

# ====== Fetch Crypto News ======
def fetch_crypto_news():
    url = f"https://cryptonews-api.com/api/v1?tickers=BTC,ETH,SOL,BNB,WLD&apikey={CRYPTO_NEWS_API_KEY}"
    resp = requests.get(url).json()
    return resp.get("data", [])

# ====== Fetch F&O Data (placeholder) ======
def fetch_fno_insights():
    # Replace with real F&O API later
    return [
        "Stock ABC: High open interest in calls",
        "Stock XYZ: F&O activity bullish",
    ]

# ====== Summarize Articles ======
def summarize_articles(articles, max_summaries=10):
    summaries = []
    for art in articles[:max_summaries]:
        title = art.get("title")
        desc = art.get("description") or ""
        summaries.append(f"{title} — {desc}")
    return summaries

# ====== Generate Predictions ======
def predict_from_news(stock_summaries, fno_data, crypto_summaries):
    predictions = []
    for title in stock_summaries:
        if "rally" in title.lower():
            predictions.append("Stocks may continue positive momentum tomorrow")
            break
    if not predictions:
        predictions.append("Stocks likely range-bound tomorrow")

    for title in crypto_summaries:
        if "surge" in title.lower() or "pump" in title.lower():
            predictions.append("Crypto (major coins) may see bullish breakout tomorrow")
            break
    if len(predictions) < 2:
        predictions.append("Crypto may consolidate tomorrow")

    return predictions

# ====== Build Daily Message ======
def build_message():
    today = datetime.date.today().strftime("%Y-%m-%d")
    message = f"📈 Daily Roundup for {today}\n\n"

    # Stocks & F&O
    stock_articles = fetch_stock_news()
    fno_info = fetch_fno_insights()
    stock_summaries = summarize_articles(stock_articles, max_summaries=10)
    message += "🧾 Stocks & F&O News:\n"
    for s in stock_summaries:
        message += f"- {s}\n"
    message += "\n📊 F&O Insights:\n"
    for item in fno_info[:5]:
        message += f"- {item}\n"
    message += "\n"

    # Crypto
    crypto_articles = fetch_crypto_news()
    crypto_summaries = summarize_articles(crypto_articles, max_summaries=10)
    message += "💰 Crypto News (BTC, ETH, SOL, BNB, WLD):\n"
    for s in crypto_summaries:
        message += f"- {s}\n"
    message += "\n"

    # Predictions
    predictions = predict_from_news(stock_summaries, fno_info, crypto_summaries)
    message += "🔮 Predictions for Tomorrow:\n"
    for p in predictions:
        message += f"- {p}\n"

    return message

# ====== Send Message to Telegram ======
def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# ====== Scheduled Job ======
def job():
    msg = build_message()
    send_message(msg)

# ====== Scheduler Thread ======
def run_scheduler():
    schedule.every().day.at("22:00").do(job)
    print("✅ Bot scheduler started. Will send daily summary at 22:00.")
    while True:
        schedule.run_pending()
        time.sleep(60)

# ====== Main ======
if __name__ == "__main__":
    # Start scheduler in a separate thread
    t = threading.Thread(target=run_scheduler)
    t.daemon = True
    t.start()
    job()

    # Start Flask to keep service alive on Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
