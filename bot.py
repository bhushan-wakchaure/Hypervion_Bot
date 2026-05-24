import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yt_dlp

# Load token from environment for safety. See .env.example
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set. Set it in the environment or create a .env file from .env.example")

async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)

    if not query:
        await update.message.reply_text("Usage: /song <name>")
        return

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

app.run_polling(drop_pending_updates=True)
