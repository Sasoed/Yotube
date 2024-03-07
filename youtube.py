import os
from telebot import TeleBot, types
from pytube import YouTube
from io import BytesIO

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота
TOKEN = '6063603462:AAFLehcN0lkP6iDVqfEGdMWHgstrUk4aJc0'
bot = TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Просто отправь мне ссылку на видео с YouTube.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    url = message.text
    try:
        yt = YouTube(url)
        title = yt.title
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
    video = yt.streams.get_highest_resolution()
    video_stream = BytesIO()
    video_stream.name = 'video.mp4'
    video.download(output_path=video_stream)
    video_stream.seek(0)
    bot.send_video(call.message.chat.id, video=video_stream)

def download_send_audio(call):
    url = call.data.split('_')[1]
    yt = YouTube(url)
    audio = yt.streams.get_audio_only()
    audio_stream = BytesIO()
    audio_stream.name = 'audio.mp3'
    audio.download(output_path=audio_stream)
    audio_stream.seek(0)
    bot.send_audio(call.message.chat.id, audio=audio_stream)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('video_'):
        download_send_video(call)
    elif call.data.startswith('audio_'):
        download_send_audio(call)

bot.polling()
