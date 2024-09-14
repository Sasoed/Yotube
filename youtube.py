import os
import yt_dlp as youtube_dl
from telebot import TeleBot, types
import time
import requests

TOKEN = 'YOUR_BOT_TOKEN'
bot = TeleBot(TOKEN)

def sanitize_filename(filename):
    return "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Просто отправь мне ссылку на видео с YouTube.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    url = message.text
    try:
        with youtube_dl.YoutubeDL({'format': 'best'}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'video'))
            thumbnail_url = info.get('thumbnail')

        markup = types.InlineKeyboardMarkup()
        video_btn = types.InlineKeyboardButton('Видео', callback_data='video_' + url)
        audio_btn = types.InlineKeyboardButton('Аудио', callback_data='audio_' + url)
        markup.add(video_btn, audio_btn)
        bot.send_photo(message.chat.id, photo=thumbnail_url, caption=f"Видео \"{title}\" было найдено.", reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке вашей ссылки. Убедитесь, что это правильная ссылка на видео YouTube.")

def download_send_video(call):
    url = call.data.split('_')[1]
    ydl_opts = {'format': 'best', 'outtmpl': '%(title)s.%(ext)s'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        video_title = sanitize_filename(info.get('title', 'video'))
        video_path = f"{video_title}.mp4"
    
    bot.send_video(call.message.chat.id, open(video_path, 'rb'))

def download_send_audio(call):
    url = call.data.split('_')[1]
    ydl_opts = {'format': 'bestaudio/best', 'outtmpl': '%(title)s.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        audio_title = sanitize_filename(info.get('title', 'audio'))
        audio_path = f"{audio_title}.mp3"
    
    bot.send_audio(call.message.chat.id, open(audio_path, 'rb'))

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('video_'):
        download_send_video(call)
    elif call.data.startswith('audio_'):
        download_send_audio(call)

def start_polling_with_retries(retries=5, delay=5):
    attempt = 0
    while attempt < retries:
        try:
            print(f"Polling attempt {attempt + 1}")
            bot.polling(none_stop=True)
            break
        except requests.exceptions.ConnectionError as e:
            attempt += 1
            print(f"ConnectionError: {e}. Attempt {attempt} of {retries}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"Unhandled exception: {e}")
            break

if __name__ == '__main__':
    start_polling_with_retries()
