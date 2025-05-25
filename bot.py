import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

API_FLASK_URL = "http://localhost:5000/generate_insight"  # Note the changed port and endpoint
TELEGRAM_BOT_TOKEN = "7694470555:AAGb_HsgKVdjAAZGUzfrMj625n_9vCJzktw"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut! Envoie-moi une question ou un prompt sur la base de connaissances.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text

    try:
        # Call Flask API with 'query' key as expected by /generate_insight endpoint
        response = requests.post(API_FLASK_URL, json={"query": user_text})

        if response.status_code == 200:
            data = response.json()
            insight = data.get("insight", "Pas de résultat retourné par le serveur.")
            await update.message.reply_text(f"Insight :\n{insight}")
        else:
            await update.message.reply_text(f"Erreur lors de l'analyse (code {response.status_code}).")
    except Exception as e:
        await update.message.reply_text(f"Erreur lors de la connexion au serveur : {e}")

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot lancé...")
    app.run_polling()

if _name_ == "_main_":
    main()