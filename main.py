import json
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters import CommandStart, Command

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=TOKEN)
dp = Dispatcher()

LINK_FILE = "config.json"

# اگر فایل لینک وجود نداشت، بسازش
if not os.path.exists(LINK_FILE):
    with open(LINK_FILE, "w", encoding="utf-8") as f:
        json.dump({"link": ""}, f)


def get_link():
    with open(LINK_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["link"]


def set_link(new_link):
    with open(LINK_FILE, "w", encoding="utf-8") as f:
        json.dump({"link": new_link}, f)


@dp.message(CommandStart())
async def start_cmd(msg: Message):
    await msg.answer("سلام 👋\nخوش اومدی!\nلطفاً اسمت رو بنویس:")
    dp.workflow_data[msg.from_user.id] = {"step": "name"}


@dp.message()
async def handle_message(msg: Message):
    user_id = msg.from_user.id
    data = dp.workflow_data.get(user_id, {})

    if data.get("step") == "name":
        data["name"] = msg.text.strip()
        data["step"] = "age"
        await msg.answer("چند سالته؟")

    elif data.get("step") == "age":
        data["age"] = msg.text.strip()
        data["step"] = "gender"
        await msg.answer("جنسیتت چیه؟ (پسر / دختر)")

    elif data.get("step") == "gender":
        data["gender"] = msg.text.strip()
        link = get_link()

        if not link:
            await msg.answer("فعلاً لینکی تنظیم نشده ❌")
            dp.workflow_data.pop(user_id, None)
            return

        btn = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔘 پیدا کردن دوست‌های اطرافم", url=link)]
        ])

        text = f"عالیه {data['name']}! 😍\nهمه‌چی آمادست، فقط روی دکمه پایین بزن تا وارد بخش دوست‌یابی بشی 👇"
        await msg.answer(text, reply_markup=btn)
        dp.workflow_data.pop(user_id, None)


@dp.message(Command("setlink"))
async def set_link_cmd(msg: Message):
    if str(msg.from_user.id) != str(ADMIN_ID):
        await msg.answer("❌ شما دسترسی به این دستور ندارید.")
        return

    parts = msg.text.split(" ", 1)
    if len(parts) == 1:
        await msg.answer("فرمت درست: /setlink <لینک>")
        return

    new_link = parts[1].strip()
    set_link(new_link)
    await msg.answer("✅ لینک با موفقیت بروزرسانی شد!")


async def main():
    dp.workflow_data = {}
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
