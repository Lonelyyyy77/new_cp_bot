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
        InlineKeyboardButton(text='Photos - 45 coins', callback_data='buy_photos')
    )
    kb.row(
        InlineKeyboardButton(text='Videos + Photos - 90 coins', callback_data='buy_videos_photos')
    )

    await callback_query.message.answer(
        '🏷️ Сейчас действует скидка 10% 🏷️\n\n'
        'Photos - 50 → 45 coins\n'
        'Videos + Photos - 100 → 90 coins',
        reply_markup=kb.as_markup()
    )


@router.callback_query(lambda c: c.data == 'buy_photos')
async def buy_photos(callback_query: CallbackQuery):
    price = 45
    link = "https://t.me/photos_channel"

    await process_purchase(callback_query, price, link)


@router.callback_query(lambda c: c.data == 'buy_videos_photos')
async def buy_videos_photos(callback_query: CallbackQuery):
    price = 90
    link = "https://t.me/videos_photos_channel"

    await process_purchase(callback_query, price, link)


async def process_purchase(callback_query: CallbackQuery, price: int, link: str):
    telegram_id = callback_query.from_user.id

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()

    if not user:
        await callback_query.message.answer('Ваш профиль не найден. Пожалуйста, зарегистрируйтесь.')
        conn.close()
        return

    user_coins = user[0]

    if user_coins >= price:
        new_balance = user_coins - price
        cursor.execute('UPDATE users SET balance = ? WHERE telegram_id = ?', (new_balance, telegram_id))
        conn.commit()

        await callback_query.message.answer(f'Спасибо за покупку! Вот ваша ссылка: {link}')
    else:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text='Пополнить', callback_data='replenish'))

        await callback_query.message.answer(
            f'Недостаточно монет! Вам нужно ещё {price - user_coins} монет. Чтобы пополнить баланс, нажмите кнопку:',
            reply_markup=kb.as_markup()
        )

    conn.close()