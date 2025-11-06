import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import os

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")  # از محیط Render می‌گیریم
ADMIN_ID = os.getenv("ADMIN_ID")  # آیدی عددی خودت

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

LINK_FILE = "config.json"

# اگر فایل لینک وجود نداشت بسازش
if not os.path.exists(LINK_FILE):
    with open(LINK_FILE, "w", encoding="utf-8") as f:
        json.dump({"link": ""}, f)

def get_link():
    with open(LINK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["link"]

def set_link(new_link):
    with open(LINK_FILE, "w", encoding="utf-8") as f:
        json.dump({"link": new_link}, f)

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    await msg.answer("سلام 👋\nخوش اومدی!\nلطفاً اسمت رو بنویس:")

    await bot.register_next_step_handler(msg, ask_age)

async def ask_age(msg: types.Message):
    name = msg.text.strip()
    msg.conf["name"] = name
    await msg.answer("چند سالته؟")
    await bot.register_next_step_handler(msg, ask_gender, name)

async def ask_gender(msg: types.Message, name):
    age = msg.text.strip()
    await msg.answer("جنسیتت چیه؟ (پسر / دختر)")
    await bot.register_next_step_handler(msg, show_link, name, age)

async def show_link(msg: types.Message, name, age):
    gender = msg.text.strip()
    link = get_link()

    if not link:
        await msg.answer("فعلاً لینکی تنظیم نشده ❌")
        return

    btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔘 پیدا کردن دوست‌های اطرافم", url=link)
    )

    text = f"عالیه {name}! 😍\nهمه‌چی آمادست، فقط روی دکمه پایین بزن تا وارد بخش دوست‌یابی بشی 👇"
    await msg.answer(text, reply_markup=btn)

# دستور فقط برای ادمین
@dp.message_handler(commands=["setlink"])
async def set_link_cmd(msg: types.Message):
    if str(msg.from_user.id) != str(ADMIN_ID):
        return await msg.answer("❌ شما دسترسی به این دستور ندارید.")

    parts = msg.text.split(" ", 1)
    if len(parts) == 1:
        return await msg.answer("فرمت درست: /setlink <لینک>")

    new_link = parts[1].strip()
    set_link(new_link)
    await msg.answer("✅ لینک با موفقیت بروزرسانی شد!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
