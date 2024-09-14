import telebot
from pytube import YouTube
from telebot import types
import os

# Инициализация бота
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(TOKEN)

# Функция для скачивания видео
def download_video(url):
    yt = YouTube(url)
    stream = yt.streams.get_highest_resolution()
    file_path = stream.download()
    return file_path

# Функция для скачивания аудио
def download_audio(url):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    file_path = stream.download()
    base, ext = os.path.splitext(file_path)
    new_file = base + '.mp3'
    os.rename(file_path, new_file)
    return new_file

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Отправь мне ссылку на YouTube видео.")

# Обработчик получения ссылки
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    # Создание кнопок для выбора
    markup = types.InlineKeyboardMarkup()
    video_button = types.InlineKeyboardButton("Скачать видео", callback_data=f"video_{url}")
    audio_button = types.InlineKeyboardButton("Скачать аудио", callback_data=f"audio_{url}")
    markup.add(video_button, audio_button)

    bot.send_message(message.chat.id, "Выбери, что ты хочешь скачать:", reply_markup=markup)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.startswith("video_"):
        url = call.data.split("_")[1]
        bot.send_message(call.message.chat.id, "Скачиваю видео, подожди немного...")
        try:
            video_file = download_video(url)
            with open(video_file, 'rb') as video:
                bot.send_video(call.message.chat.id, video)
            os.remove(video_file)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка: {e}")
    elif call.data.startswith("audio_"):
        url = call.data.split("_")[1]
        bot.send_message(call.message.chat.id, "Скачиваю аудио, подожди немного...")
        try:
            audio_file = download_audio(url)
            with open(audio_file, 'rb') as audio:
                bot.send_audio(call.message.chat.id, audio)
            os.remove(audio_file)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Ошибка: {e}")

# Запуск бота
bot.polling(none_stop=True)
