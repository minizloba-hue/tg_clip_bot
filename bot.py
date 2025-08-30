import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Загружаем переменные из .env
load_dotenv()

# Переменные окружения
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GSHEET_KEY = os.getenv('GSHEET_KEY')
SHEET_NAME = os.getenv('SHEET_NAME')
ADMIN_ID = os.getenv('ADMIN_ID')

# Создаем бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Функция для работы с Google Sheets
def get_google_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GSHEET_KEY, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1  # Открываем первую таблицу
    return sheet

# Функция старта
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я твой бот для поиска фильмов.")

# Функция для добавления фильма (только для админа)
@dp.message_handler(commands=['addfilm'])
async def add_film(message: types.Message):
    if str(message.from_user.id) != ADMIN_ID:
        await message.answer("У вас нет доступа к этой команде.")
        return
    # Пример добавления фильма (добавить правильную логику)
    sheet = get_google_sheet()
    sheet.append_row(['example_code', 'example_title', 'example_banner', 'example_link'])
    await message.answer("Фильм добавлен!")

# Запуск бота
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
