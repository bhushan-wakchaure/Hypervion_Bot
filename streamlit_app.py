import streamlit as st
import os
from threading import Thread
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_bot_token():
    # Streamlit Cloud secrets (preferred)
    try:
        return st.secrets["BOT_TOKEN"]
    except (KeyError, FileNotFoundError):
        pass
    # Fallback to env variable (local .env)
    return os.getenv("BOT_TOKEN")

QUERY_LOG_FILE = "query_log.json"


def load_queries():
    if os.path.exists(QUERY_LOG_FILE):
        with open(QUERY_LOG_FILE, "r") as f:
            return json.load(f)
    return []


def save_query(query):
    queries = load_queries()
    queries.append(query)
    with open(QUERY_LOG_FILE, "w") as f:
        json.dump(queries, f)


def run_bot():
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
    import yt_dlp

    BOT_TOKEN = get_bot_token()
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN not found. Set it in Streamlit secrets or .env file.")
        return

    async def song(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = " ".join(context.args)
        if not query:
            await update.message.reply_text("Usage: /song <name>")
            return

        save_query(query)
        print(f"{len(load_queries())}. {query}")

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
    print("Bot started polling...")
    app.run_polling(drop_pending_updates=True)


if "bot_started" not in st.session_state:
    st.session_state.bot_started = True
    Thread(target=run_bot, daemon=True).start()

st.title("Hyperion Bot")
token = get_bot_token()
if token:
    st.success("Telegram bot is running!")
else:
    st.error("BOT_TOKEN not found! Add it in Settings > Secrets on Streamlit Cloud.")
st.write("Send `/song <name>` to the bot on Telegram.")

st.subheader("Song Queries")
queries = load_queries()
if queries:
    for i, q in enumerate(queries, 1):
        st.write(f"{i}. {q}")
else:
    st.info("No queries yet.")

col1, col2 = st.columns(2)
with col1:
    if st.button("Refresh"):
        st.rerun()
with col2:
    if st.button("Clear Log"):
        if os.path.exists(QUERY_LOG_FILE):
            os.remove(QUERY_LOG_FILE)
        st.rerun()
