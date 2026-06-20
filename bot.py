import os
import logging
from anthropic import Anthropic
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

client = Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """Ти — дружній асистент для роздачі бонусів. Спілкуєшся виключно українською мовою.

Твоя головна задача — допомагати клієнтам отримати бонус та відповідати на їхні запитання.

Як клієнт отримує бонус:
- Клієнту потрібно написати фразу "Я готова/готовий, давайте" — і бонус буде надано.

Якщо клієнт запитує як отримати бонус — поясни йому це просто і дружньо.
Якщо клієнт написав "Я готова" або "Я готовий" або "давайте" — підтвердь отримання) і скажи що бонус вже зараховано.

Будь коротким, привітним в позитивним. Не вигадуй деталі якихне не знаєш."""

user_histories: dict[int, list] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привіт! 👋 Я допоможу тобі отримати бонусилите на днів частини!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    if user_id not in user_histories:
        user_histories[user_id] = []
    user_histories[user_id].append({"role":"user","content":user_message})
    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]
    try:
        response = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=500,system=SYSTEM_PROMPT,messages=user_histories[user_id])
        reply = response.content[0].text
        user_histories[user_id].append({"role":"assistant","content":reply})
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text("Вибачте, сталася помилка.")

def main():
    app = Application.builder().token(os.environ["TELEGRAM_TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
