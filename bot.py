from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

from flask import Flask
from threading import Thread
import requests
import os
from dotenv import load_dotenv

# Load variables from .env file if present
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# FLASK WEB SERVER
# =========================

app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot Running"


def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)


Thread(target=run_web).start()
async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Usage: /song <name>")
        return

    # ydl_opts = {
    #     'format': 'bestaudio/best',
    #     'outtmpl': '%(title)s.%(ext)s',
    #     'quiet': True
    # }
    ydl_opts = {
    "format": "bestaudio/best",
    "outtmpl": "%(title)s.%(ext)s",
    "quiet": True,
    "noplaylist": True,
    "cookiefile": "cookies.txt"
}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        filename = ydl.prepare_filename(info)

    await update.message.reply_audio(audio=open(filename, 'rb'))

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("song", song))

app.run_polling()
