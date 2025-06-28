import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN")
BUY_LIMIT = 88.6  # Можно менять через команду

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот запущен. Жду возможности арбитража...")

async def set_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global BUY_LIMIT
    try:
        BUY_LIMIT = float(context.args[0])
        await update.message.reply_text(f"Лимит на покупку теперь: {BUY_LIMIT} KGS")
    except:
        await update.message.reply_text("Ошибка: введите лимит числом, например /setlimit 88.50")

async def profit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text.replace('/profit', '').strip()
        parts = dict(part.split('=') for part in text.split())

        buy_price = float(parts['купил'])
        sell_price = float(parts['продал'])
        amount = float(parts['сумма'])

        spent = buy_price * amount
        earned = sell_price * amount
        profit = earned - spent
        status = "ПРИБЫЛЬ" if profit > 0 else "УБЫТОК"

        await update.message.reply_text(
            f"📊 {status}:\n"
            f"• Куплено: {amount} USDT по {buy_price} = {spent:.2f} KGS\n"
            f"• Продажа по {sell_price} = {earned:.2f} KGS\n"
            f"• Разница: {profit:.2f} KGS"
        )

    except Exception as e:
        logger.error(e)
        await update.message.reply_text("❌ Ошибка. Формат: /profit купил=88.50 продал=84.10 сумма=11.29")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlimit", set_limit))
    app.add_handler(CommandHandler("profit", profit))
    print("Бот запущен.")
    app.run_polling()
