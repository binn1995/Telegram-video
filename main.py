import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from yt_dlp import YoutubeDL
import requests

# ---------------------------- CONFIG ----------------------------
TOKEN = os.getenv("7841149691:AAGXNDAGkoEo7X4uKpYbwuhLLwMEgvEO19Q")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

logging.basicConfig(level=logging.INFO)

# -------------------------- YT-DLP SETUP -------------------------
def download_video(url, platform):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

# ------------------------ MESSAGE HANDLER ------------------------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Simple platform detection
    platform = None
    if any(x in url for x in ["tiktok.com", "douyin.com"]):
        platform = "TikTok"
    elif any(x in url for x in ["facebook.com", "fb.watch"]):
        platform = "Facebook"
    elif "twitter.com" in url or "x.com" in url:
        platform = "Twitter"
    elif any(x in url for x in ["youtube.com", "youtu.be"]):
        platform = "YouTube"

    if not platform:
        await update.message.reply_text("❌ Không nhận diện được nền tảng từ liên kết bạn gửi.")
        return

    await update.message.reply_text(f"⏳ Đang tải video từ {platform}...")
    try:
        video_path = download_video(url, platform)
        await update.message.reply_video(video=open(video_path, 'rb'))
        os.remove(video_path)  # Dọn file sau khi gửi
    except Exception as e:
        logging.error(f"Lỗi tải video: {e}")
        await update.message.reply_text(f"❌ Lỗi khi tải video: {e}")

# ---------------------------- MAIN APP ----------------------------
