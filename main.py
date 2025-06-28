import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

import os

# Получаем токен из переменной среды (удобно для Railway/Render)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Лимит на покупку USDT (можешь менять)
BUY_LIMIT = 88.80

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Получение лучшей цены покупки USDT в KGS (Bybit P2P)
async def get_buy_price():
    url = "https://api2.bybit.com/fiat/otc/v1/trading-pairs?userId=0&tokenId=USDT&currencyId=KGS&payment=all&side=buy&size=5&page=1"
    response = requests.get(url, timeout=10)
    print("Raw response:", response.text)  # <-- Эта строка для диагностики!
    data = response.json()
    items = data.get("result", {}).get("items", [])
    if not items:
        raise Exception("Нет подходящих объявлений на покупку USDT за KGS.")
    best = items[0]
    return float(best["price"])

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Жду возможности арбитража...")

# /check
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BUY_LIMIT
    try:
        price = await get_buy_price()
        if price < BUY_LIMIT:
            await update.message.reply_text(
                f"ВНИМАНИЕ! Цена USDT ниже лимита: {price} KGS (лимит {BUY_LIMIT})"
            )
        else:
            await update.message.reply_text(
                f"Текущий курс покупки: {price} KGS (лимит {BUY_LIMIT})"
            )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при получении курса: {e}")

# /setlimit 88.60
async def setlimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BUY_LIMIT
    try:
        new_limit = float(context.args[0])
        BUY_LIMIT = new_limit
        await update.message.reply_text(f"Лимит на покупку теперь: {BUY_LIMIT} KGS")
    except Exception:
        await update.message.reply_text("Используй так: /setlimit 88.60")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("setlimit", setlimit))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
