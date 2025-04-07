import os
import re
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from bs4 import BeautifulSoup
from pytube import YouTube
from instaloader import Instaloader, Post
from TikTokApi import TikTokApi
from dotenv import load_dotenv
import logging

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TELEGRAM_TOKEN = os.getenv('7527429868:AAGcBlm_obLae3TwWnPpDyzlcnhy9UYv6QA')

# Khởi tạo thành phần
L = Instaloader()
api = TikTokApi()

async def handle_message(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    url = update.message.text

    try:
        # Kiểm tra URL hợp lệ
        if not re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', url):
            await update.message.reply_text("❌ Link không hợp lệ!")
            return

        # Xác định nền tảng và tải video
        if "tiktok" in url:
            filename = await download_tiktok(url)
        elif "facebook" in url:
            filename = await download_facebook(url)
        elif "youtube" in url or "youtu.be" in url:
            filename = await download_youtube(url)
        elif "instagram" in url:
            filename = await download_instagram(url)
        elif "twitter" in url or "x.com" in url:
            filename = await download_twitter(url)
        else:
            await update.message.reply_text("⚠️ Nền tảng chưa được hỗ trợ!")
            return

        # Gửi video về
        await update.message.reply_video(video=open(filename, 'rb'))
        
        # Xoá link người dùng NGAY KHI GỬI VIDEO THÀNH CÔNG
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            logger.info(f"Đã xoá tin nhắn của user {user.id}")
        except Exception as e:
            logger.error(f"Lỗi xoá tin nhắn: {str(e)}")

        # Dọn dẹp file
        os.remove(filename)

    except Exception as e:
        error_msg = f"❌ Lỗi: {str(e)}"
        logger.error(error_msg)
        await update.message.reply_text(error_msg)

# ... (Các hàm download_tiktok, download_facebook,... giữ nguyên như code trước) ...

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "🖐️ Chào bạn! Gửi link video từ:\n"
        "- TikTok/Douyin\n- Facebook\n- YouTube/Shorts\n- Instagram\n- Twitter/X\n"
        "và tôi sẽ tải xuống giúp bạn!\n\n"
        "⚠️ Link của bạn sẽ được tự động xoá sau khi tải xong!"
    )

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logger.info("🤖 Bot đang chạy...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()