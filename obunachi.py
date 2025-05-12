import asyncio
import aiosqlite
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardRemove

API_TOKEN = '7813937733:AAHtgxXK1eNXVxX0nhAZk-dcMEFV3jyuhhI'  # @BotFather dan olingan token

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

DB_PATH = "referrals.db"

# Baza yaratish
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                invited_by INTEGER,
                invites INTEGER DEFAULT 0
            )
        ''')
        await db.commit()

@dp.message(CommandStart(deep_link=True))
async def start_with_referral(message: Message, command: CommandStart):
    referrer_id = command.args
    user_id = message.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        user = await db.execute_fetchone("SELECT * FROM users WHERE user_id = ?", (user_id,))
        if user is None:
            await db.execute("INSERT INTO users (user_id, invited_by) VALUES (?, ?)", (user_id, referrer_id))
            await db.execute("UPDATE users SET invites = invites + 1 WHERE user_id = ?", (referrer_id,))
            await db.commit()
            await message.answer("Siz muvaffaqiyatli ro'yxatdan o'tdingiz referal orqali!")
        else:
            await message.answer("Siz allaqachon ro'yxatdan o'tgansiz.")

    await send_referral_link(message)

@dp.message(CommandStart())
async def start(message: Message):
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        user = await db.execute_fetchone("SELECT * FROM users WHERE user_id = ?", (message.from_user.id,))
        if user is None:
            await db.execute("INSERT INTO users (user_id) VALUES (?)", (message.from_user.id,))
            await db.commit()
            await message.answer("Xush kelibsiz! Siz endi ro'yxatdan o'tdingiz.")
        else:
            await message.answer("Yana xush kelibsiz!")

    await send_referral_link(message)

async def send_referral_link(message: Message):
    bot_username = (await bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={message.from_user.id}"
    await message.answer(f"Sizning referal havolangiz:\n{referral_link}")

@dp.message()
async def unknown(message: Message):
    await message.answer("Iltimos /start buyrug'ini foydalaning.")

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
