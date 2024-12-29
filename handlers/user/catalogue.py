import sqlite3

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import DB_NAME

router = Router()


@router.callback_query(lambda c: c.data == 'catalogue')
async def show_catalogue(callback_query: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text='Photos - 50 coins', callback_data='product_photos_50')
    )
    kb.row(
        InlineKeyboardButton(text='Videos + Photos - 100 coins', callback_data='product_videos_photos_100')
    )

    await callback_query.message.answer('Выберите продукт из каталога:', reply_markup=kb.as_markup())


@router.callback_query(lambda c: c.data.startswith('product_'))
async def handle_product_selection(callback_query: CallbackQuery):
    data = callback_query.data.split('_')
    price = int(data[2])

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE telegram_id = ?', (callback_query.from_user.id,))
    user = cursor.fetchone()

    if not user:
        await callback_query.message.answer('Ваш профиль не найден. Пожалуйста, зарегистрируйтесь.')
        conn.close()
        return

    user_coins = user[0]

    if user_coins >= price:
        new_balance = user_coins - price
        cursor.execute('UPDATE users SET balance = ? WHERE telegram_id = ?', (new_balance, callback_query.from_user.id))
        conn.commit()

        link = 'https://t.me/example_channel'
        await callback_query.message.answer(f'Спасибо за покупку! Вот ваша ссылка: {link}')
    else:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text='Пополнить', callback_data='replenish'))

        await callback_query.message.answer(
            f'Недостаточно монет! Вам нужно {price - user_coins} монет. Чтоб пополнить нажмите кнопку:',
            reply_markup=kb.as_markup())

    conn.close()
