import os
from telebot import TeleBot, types
from pytube import YouTube
from io import BytesIO

TOKEN = 'YOUR_BOT_TOKEN'
bot = TeleBot(TOKEN)

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Просто отправь мне ссылку на видео с YouTube.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    url = message.text
    try:
        yt = YouTube(url)
        title = sanitize_filename(yt.title)

        # Создаем директорию с названием видео, если она не существует
        if not os.path.exists(title):
            os.makedirs(title)

        thumbnail_url = yt.thumbnail_url
        markup = types.InlineKeyboardMarkup()
        video_btn = types.InlineKeyboardButton('Видео', callback_data='video_' + url)
        audio_btn = types.InlineKeyboardButton('Аудио', callback_data='audio_' + url)
        markup.add(video_btn, audio_btn)

        bot.send_photo(message.chat.id, photo=thumbnail_url, caption=f"Видео \"{title}\" было найдено.", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке вашей ссылки. Убедитесь, что это правильная ссылка на видео YouTube.")

def download_send_video(call):
    url = call.data.split('_')[1]
    yt = YouTube(url)
    title = sanitize_filename(yt.title)
    video = yt.streams.get_highest_resolution()

    video_path = os.path.join(title, 'video.mp4')
    if not os.path.exists(video_path):
        video.download(output_path=title, filename='video.mp4')

    bot.send_video(call.message.chat.id, open(video_path, 'rb'))

def download_send_audio(call):
    url = call.data.split('_')[1]
    yt = YouTube(url)
    title = sanitize_filename(yt.title)
    audio = yt.streams.get_audio_only()

    audio_path = os.path.join(title, 'audio.mp3')
    if not os.path.exists(audio_path):
        audio.download(output_path=title, filename='audio.mp3')

    bot.send_audio(call.message.chat.id, open(audio_path, 'rb'))

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('video_'):
        download_send_video(call)
    elif call.data.startswith('audio_'):
        download_send_audio(call)

bot.polling()
