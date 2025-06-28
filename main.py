import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN", "TOKEN_NOT_SET")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def get_price():
    try:
        headers = {"Content-Type": "application/json"}
        buy_payload = {
            "userId": "",
            "tokenId": "USDT",
            "currencyId": "KGS",
            "payment": [],
            "side": "BUY",
            "size": 1,
            "page": 1
        }
        sell_payload = {
            "userId": "",
            "tokenId": "USDT",
            "currencyId": "KGS",
            "payment": [],
            "side": "SELL",
            "size": 1,
            "page": 1
        }

        buy_response = requests.post("https://api2.bybit.com/fiat/otc/item/online", json=buy_payload, headers=headers, timeout=10)
        buy_data = buy_response.json()
        sell_response = requests.post("https://api2.bybit.com/fiat/otc/item/online", json=sell_payload, headers=headers, timeout=10)
        sell_data = sell_response.json()

        if "result" in buy_data and "items" in buy_data["result"] and len(buy_data["result"]["items"]) > 0:
            buy_price = float(buy_data["result"]["items"][0]["price"])
        else:
            buy_price = None

        if "result" in sell_data and "items" in sell_data["result"] and len(sell_data["result"]["items"]) > 0:
            sell_price = float(sell_data["result"]["items"][0]["price"])
        else:
            sell_price = None

        if buy_price is None and sell_price is None:
            return "Нет подходящих объявлений на покупку и продажу USDT за KGS."
        elif buy_price is None:
            return f"Нет объявлений на покупку USDT за KGS. Продажа: {sell_price} KGS."
        elif sell_price is None:
            return f"Покупка USDT: {buy_price} KGS. Нет объявлений на продажу."
        else:
            return f"Курс USDT: покупка {buy_price} KGS, продажа {sell_price} KGS"

    except Exception as e:
        return f"Ошибка при получении курса:\n{str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Жду возможности арбитража...")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = await get_price()
    await update.message.reply_text(price)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
