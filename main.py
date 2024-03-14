import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from moviepy.editor import VideoFileClip
import requests

# Инициализация логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Привет! Я бот для конвертации видео в GIF. Просто отправь мне видео или ссылку на видео, и я создам GIF для тебя.')

# Обработчик текстовых сообщений
def convert_to_gif(update: Update, context: CallbackContext) -> None:
    # Получаем объект сообщения
    message = update.message
    # Проверяем, есть ли вложенный документ
    if message.document and message.document.mime_type.startswith('video'):
        # Получаем файл видео
        video_file = message.document.get_file()
        # Создаем путь к временному файлу видео
        video_filename = "video" + os.path.splitext(message.document.file_name)[1]
        # Скачиваем видео
        video_file.download(video_filename)
        # Конвертируем видео в GIF
        gif_path = convert_video_to_gif(video_filename)
        # Отправляем уведомление о завершении конвертации
        send_conversion_notification(message, gif_path)
    elif message.text.startswith('http') and message.text.endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv')):
        # Получаем ссылку на видео
        video_url = message.text
        # Определяем формат видео по расширению ссылки
        video_format = os.path.splitext(video_url)[1][1:].lower()
        # Создаем путь к временному файлу видео
        video_filename = "video_from_url." + video_format
        # Загружаем видео с помощью ссылки
        download_video_from_url(video_url, video_filename)
        # Конвертируем видео в GIF
        gif_path = convert_video_to_gif(video_filename)
        # Отправляем уведомление о завершении конвертации
        send_conversion_notification(message, gif_path)
    else:
        update.message.reply_text('Пожалуйста, отправьте видео или ссылку на видео.')

# Функция для загрузки видео с помощью ссылки
def download_video_from_url(video_url: str, filename: str) -> None:
    with open(filename, 'wb') as f:
        response = requests.get(video_url)
        f.write(response.content)

# Функция для конвертации видео в GIF
def convert_video_to_gif(video_filename: str) -> str:
    # Генерируем имя GIF файла
    gif_filename = os.path.splitext(video_filename)[0] + ".gif"
    try:
        # Конвертируем видео в GIF
        video_clip = VideoFileClip(video_filename)
        video_clip.write_gif(gif_filename, program="ffmpeg")
        return gif_filename
    except Exception as e:
        logger.error(f"Ошибка при конвертации видео в GIF: {e}")
        return None

# Функция для отправки уведомления о завершении конвертации
def send_conversion_notification(message: Update, gif_path: str) -> None:
    if gif_path:
        message.reply_text('Конвертация завершена! Ваш GIF доступен по этой ссылке:')
        message.reply_document(open(gif_path, 'rb'))
    else:
        message.reply_text('Произошла ошибка при конвертации видео в GIF. Пожалуйста, попробуйте снова.')

def main() -> None:
    # Замените 'YOUR_API_KEY' на ваш API-ключ
    updater = Updater("YOUR_API_KEY")

    dispatcher = updater.dispatcher

    # Добавляем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))

    # Добавляем обработчик текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), convert_to_gif))

    # Добавляем обработчик вложенных документов (видео)
    dispatcher.add_handler(MessageHandler(Filters.document.video, convert_to_gif))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
