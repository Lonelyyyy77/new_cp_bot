import sqlite3

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import DB_NAME
from database.user.user import add_replenishment_request

router = Router()


@router.callback_query(lambda c: c.data == 'replenish')
async def replenish(callback_query: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='100', callback_data='rp_100'))
    kb.add(InlineKeyboardButton(text='500', callback_data='rp_500'))
    kb.add(InlineKeyboardButton(text='1000', callback_data='rp_1000'))

    await callback_query.message.answer("Сhoose the amount of coins", reply_markup=kb.as_markup())


@router.callback_query(lambda c: c.data.startswith('rp_'))
async def process_replenish(callback_query: CallbackQuery):
    amount = int(callback_query.data.split('_')[-1])
    telegram_id = callback_query.from_user.id

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT ref_link, reffed_by_worker FROM users WHERE telegram_id = ?
    ''', (telegram_id,))
    user_data = cursor.fetchone()

    if user_data:
        referral_link, worker_name = user_data
    else:
        referral_link, worker_name = None, None

    cursor.execute('''
        INSERT INTO replenishment_requests (telegram_id, amount, referral_link, worker_name, status)
        VALUES (?, ?, ?, ?, 'pending')
    ''', (telegram_id, amount, referral_link, worker_name))
    conn.commit()
    conn.close()

    await callback_query.message.answer(
        f"Please wait, the administrator will contact you for replenishing {amount} coins."
    )