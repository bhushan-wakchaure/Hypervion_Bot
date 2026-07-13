import streamlit as st
import os
from threading import Thread
from dotenv import load_dotenv

load_dotenv()


def run_bot():
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
    import yt_dlp

    BOT_TOKEN = os.getenv("BOT_TOKEN")

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
            "cookiefile": "cookies.txt",
        }

        filename = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{query}", download=True)[
                    "entries"
                ][0]
                filename = ydl.prepare_filename(info)

            with open(filename, "rb") as audio_file:
                await update.message.reply_audio(audio=audio_file)
        except Exception as e:
            await update.message.reply_text(f"Error: {e}")
        finally:
            if filename and os.path.exists(filename):
                os.remove(filename)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("song", song))
    app.run_polling()


if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    Thread(target=run_bot, daemon=True).start()

st.title("Hyperion Bot")
st.success("Telegram bot is running!")
st.write("Send `/song <name>` to the bot on Telegram.")
