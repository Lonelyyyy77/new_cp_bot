import sqlite3

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import DB_NAME

router = Router()


@router.callback_query(lambda c: c.data == 'office')
async def office(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT name, users_reffered, balance FROM workers WHERE telegram_id = ?', (telegram_id,))
    worker_info = cursor.fetchone()

    if worker_info:
        name, users_referred, balance = worker_info

        cursor.execute('SELECT telegram_id FROM users WHERE reffed_by_worker = ?', (telegram_id,))
        referred_users = cursor.fetchall()

        # referred_user_ids = [str(user[0]) for user in referred_users]

        message_text = (
            f"Вы в кабинете воркера: {name}\n"
            f"Количество зареференных пользователей: {users_referred}\n"
            f"Баланс: {balance} монет\n\n"
        )

        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text='Реферальная система', callback_data='referral_system'))

        await callback_query.message.answer(message_text, reply_markup=kb.as_markup())
    else:
        await callback_query.message.answer("Вы не являетесь воркером.")

    conn.close()


