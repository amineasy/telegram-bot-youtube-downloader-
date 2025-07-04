import os
from decouple import config
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from database.db import SessionLocal, init_db
from database.models import Download
from services.download_service import add_download
from services.youtube_service import YouTubeService
from services.user_service import get_or_create_user


token = config('TOKEN')


init_db()



bot = telebot.TeleBot(token)

yt_service = YouTubeService()

user_downloads = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! لینک یوتیوب رو بفرست تا کیفیت‌ها رو برات بفرستم.")

@bot.message_handler(func=lambda message: True)
def handle_link(message):


    user_id = message.from_user.id

    user = get_or_create_user(user_id)

    link = message.text.strip()

    if not (
        link.startswith("https://www.youtube.com") or
        link.startswith("http://www.youtube.com") or
        link.startswith("https://youtu.be") or
        link.startswith("http://youtu.be")
    ):
        bot.send_message(user_id, "❌ لطفا فقط لینک معتبر یوتیوب ارسال کن.")
        return

    try:
        qualities = yt_service.get_available_qualities(link)

        if not qualities:
            qualities = ['medium']

        user_downloads[user_id] = {'link': link, 'qualities': qualities}

        markup = InlineKeyboardMarkup()
        for quality in qualities:
            markup.add(InlineKeyboardButton(text=quality, callback_data=f'download_{quality}'))

        bot.send_message(user_id, "✅ لطفاً کیفیت مورد نظر رو انتخاب کن:", reply_markup=markup)

    except Exception as e:
        bot.send_message(user_id, f"⚠️ خطا در دریافت کیفیت‌ها: {str(e)}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('download_'))
def callback_download(call):
    user_id = call.from_user.id




    quality = call.data.split('_')[1]

    if user_id not in user_downloads:
        bot.answer_callback_query(call.id, "⚠️ لطفا ابتدا یک لینک ارسال کن.")
        return

    link = user_downloads[user_id]['link']
    bot.answer_callback_query(call.id, f"⬇️ در حال دانلود با کیفیت {quality}...")

    user = get_or_create_user(user_id)
    add_download(user.id, link, quality)

    try:
        filepath = yt_service.download(link, user_id, quality)

        with open(filepath, 'rb') as video:
            bot.send_video(user_id, video)

        os.remove(filepath)

    except Exception as e:
        bot.send_message(user_id, f"🚫 خطا در دانلود: {str(e)}")




@bot.message_handler(commands=['history'])
def send_history(message):
    user_id = message.from_user.id
    user = get_or_create_user(user_id)
    db = SessionLocal()
    downloads = db.query(Download).filter(Download.user_id == user.id).order_by(Download.timestamp.desc()).limit(10).all()
    db.close()

    if not downloads:
        bot.send_message(user_id, "شما هنوز هیچ دانلودی انجام نداده‌اید.")
        return

    markup = InlineKeyboardMarkup()
    for d in downloads:
        markup.add(InlineKeyboardButton(text=f"{d.link} ({d.quality})", callback_data=f"history_{d.id}"))

    bot.send_message(user_id, "تاریخچه دانلودهای شما:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('history_'))
def callback_history(call):
    user_id = call.from_user.id
    download_id = int(call.data.split('_')[1])
    db = SessionLocal()
    download = db.query(Download).filter(Download.id == download_id, Download.user.has(telegram_id=user_id)).first()
    db.close()

    if not download:
        bot.answer_callback_query(call.id, "دانلود یافت نشد یا اجازه دسترسی ندارید.")
        return

    bot.answer_callback_query(call.id, f"در حال دانلود مجدد: {download.link}")

    try:
        filepath = yt_service.download(download.link, user_id, download.quality)
        with open(filepath, 'rb') as video:
            bot.send_video(user_id, video)
        os.remove(filepath)
    except Exception as e:
        bot.send_message(user_id, f"خطا در دانلود: {str(e)}")


bot.infinity_polling()
