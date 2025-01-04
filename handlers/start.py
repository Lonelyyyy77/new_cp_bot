from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.user.user import get_user_status, add_user, get_user_balance

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    referral_code = message.text.split()[-1] if len(message.text.split()) > 1 else None

    status = get_user_status(telegram_id)
    balance = get_user_balance(telegram_id)

    if status == "admin":
        admin_kb = InlineKeyboardBuilder()
        admin_kb.row(InlineKeyboardButton(text='🛒 Каталог', callback_data='catalogue'))
        admin_kb.row(InlineKeyboardButton(text='👨‍💼 Админ панель', callback_data='admin_panel'))
        admin_kb.row(InlineKeyboardButton(text='🔗 Кабинет', callback_data='office'))

        await message.answer("😊 Добро пожаловать, администратор! У вас есть доступ ко всем функциям.",
                             reply_markup=admin_kb.as_markup())
    elif status == "worker":
        worker_kb = InlineKeyboardBuilder()
        worker_kb.row(InlineKeyboardButton(text='🛒 Каталог', callback_data='catalogue'))
        worker_kb.row(InlineKeyboardButton(text='👨‍💼 Кабинет', callback_data='office'))

        await message.answer("[🥷] Привет, воркер! Удачной работы.", reply_markup=worker_kb.as_markup())
    elif status == "user":
        user_kb = InlineKeyboardBuilder()
        user_kb.add(InlineKeyboardButton(text='Каталог Товаров', callback_data='catalogue'))
        user_kb.row(InlineKeyboardButton(text='Тех. Поддержка', callback_data='help'))
        user_kb.row(InlineKeyboardButton(text='Баланс', callback_data='replenish'))

        await message.answer(f"❤️ Привет, пользователь! Рады видеть вас снова.\n\nВаш баланс: {balance} монет.",
                             reply_markup=user_kb.as_markup())
    else:
        await add_user(telegram_id, username, referral_code)
        user_kb = InlineKeyboardBuilder()
        user_kb.add(InlineKeyboardButton(text='Каталог Товаров', callback_data='catalogue'))
        user_kb.row(InlineKeyboardButton(text='Тех. Поддержка', callback_data='help'))
        user_kb.row(InlineKeyboardButton(text='Баланс', callback_data='replenish'))

        await message.answer("❤️ Добро пожаловать! \n🧸 Тут ты сможешь купить тот самый качественный материал за небольшую цену! 🧸 ",
                             reply_markup=user_kb.as_markup())
