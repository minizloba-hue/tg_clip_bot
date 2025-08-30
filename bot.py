import os
import asyncio
import logging
import gspread
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

# Загружаем переменные из .env
load_dotenv()
API_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
GSHEET_KEY = os.getenv("GSHEET_KEY")
SHEET_NAME = os.getenv("SHEET_NAME")

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Подключение к Google Sheets
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GSHEET_KEY, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Локальное хранилище данных
db = {}

# Функция обновления базы
async def update_db():
    global db
    records = sheet.get_all_records()
    # ключ = code, значение = словарь с title, banner, ref_link
    db = {
        str(row["code"]).strip(): {
            "title": str(row["title"]).strip(),
            "banner": str(row["banner"]).strip(),
            "ref_link": str(row["ref_link"]).strip()
        }
        for row in records if row.get("code")
    }
    logging.info(f"База обновлена. {len(db)} записей.")

# Автообновление каждые 10 минут
async def auto_update():
    while True:
        try:
            await update_db()
        except Exception as e:
            logging.error(f"Ошибка автообновления: {e}")
        await asyncio.sleep(600)

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет! Отправь мне код, и я дам тебе название, баннер и реферальную ссылку 🚀")

# Команда /update (только для админа)
@dp.message_handler(commands=["update"])
async def manual_update(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await update_db()
        await message.answer("✅ База обновлена вручную.")
    else:
        await message.answer("❌ У тебя нет прав на эту команду.")

# Обработка кодов
@dp.message_handler()
async def send_clip_info(message: types.Message):
    code = message.text.strip()
    if code in db:
        item = db[code]
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton(text="Перейти по ссылке", url=item["ref_link"]))
        await message.answer(f"Название: {item['title']}", reply_markup=kb)
        if item["banner"]:
            await message.answer_photo(item["banner"])
    else:
        await message.answer("❌ Код не найден. Проверь правильность ввода.")

# Старт бота
async def on_startup(dp):
    await update_db()
    asyncio.create_task(auto_update())

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
