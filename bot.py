import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import TOKEN
from database import create_db
from database.admin.admin import add_admin

from handlers.user.routers import user_routers
from handlers.admin.routers import admin_routers
from handlers.worker.routers import worker_routers

from handlers.start import router as start_router


router = Router()

logging.basicConfig(level=logging.INFO)


@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Привет! Я твой бот и отвечаю только на команду /start.")


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    create_db()
    add_admin(6588562022)
    add_admin(1054908749)

    await admin_routers(dp)
    await user_routers(dp)
    await worker_routers(dp)

    dp.include_router(start_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
