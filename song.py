import telebot
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import youtube_dl
import os

# Укажите свои учетные данные Spotify
spotify_client_id = '8109be486ca74251b67bda92e66e49a4'
spotify_client_secret = '15c97e98592148a29aafe009c6b191bb'

# Создание экземпляра Telebot с вашим токеном
bot = telebot.TeleBot("7012769971:AAElpqfUKir1y11UuVND1dN3T4FQQ0A43Wg")

# Подключение к API Spotify
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret))

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я могу помочь тебе найти музыку. Просто отправь мне название песни или часть текста.")

# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def find_music(message):
    try:
        query = message.text
        # Ищем первый трек по запросу в Spotify
        result = sp.search(q=query, type='track', limit=1)

        if result['tracks']['items']:
            track = result['tracks']['items'][0]
            # Получаем название песни и артиста
            song_name = track['name']
            artist_name = track['artists'][0]['name']
            # Ищем полную версию песни на YouTube
            search_query = f"{song_name} {artist_name} official audio"
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"{song_name}.%(ext)s",
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(f"ytsearch:{search_query}", download=False)['entries'][0]
                song_url = info_dict['url']
                # Скачиваем аудиофайл и конвертируем его в mp3
                os.system(f"youtube-dl --extract-audio --audio-format mp3 -o '{song_name}.%(ext)s' '{song_url}'")
            # Отправляем пользователю аудиофайл
            bot.send_audio(message.chat.id, open(f"{song_name}.mp3", 'rb'))
            # Удаляем временный файл
            os.remove(f"{song_name}.mp3")
        else:
            bot.reply_to(message, "К сожалению, не удалось найти трек по вашему запросу.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

# Запуск бота
bot.polling()
