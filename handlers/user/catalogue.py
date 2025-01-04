import sqlite3

from aiogram import Router, Bot
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import TOKEN
from database import DB_NAME
from database.admin.admin import get_admin_id

router = Router()

async def save_link_request(telegram_id: int, channel_name: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    message = f"🛡 Запрос на ссылку канала {channel_name} от пользователя ID {telegram_id}"

    cursor.execute('''
        INSERT INTO link_requests (telegram_id, channel_name, message)
        VALUES (?, ?, ?)
    ''', (telegram_id, channel_name, message))
    conn.commit()
    conn.close()

    admin_id = get_admin_id()
    if admin_id:
        kb = InlineKeyboardBuilder()
        kb.row(InlineKeyboardButton(text='🔑 Посмотреть запросы на ссылки', callback_data='view_link_request'))

        bot = Bot(token=TOKEN)
        await bot.send_message(
            admin_id,
            f"🔑 Пользователь с ID {telegram_id} запросил ссылку на канал: {channel_name}.",
            reply_markup=kb.as_markup()
        )


@router.callback_query(lambda c: c.data == 'catalogue')
async def show_catalogue(callback_query: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text='Photos Only - 45 💎', callback_data='buy_photos')
    )
    kb.row(
        InlineKeyboardButton(text='Videos + Photos - 90 💎', callback_data='buy_videos_photos')
    )

    await callback_query.message.answer(
        '🏷️ Сейчас действует скидка 10%! 🏷️\n\n'
        'Photos - 50 → 45 💎\n'
        'Videos + Photos - 100 → 90 💎',
        reply_markup=kb.as_markup()
    )


@router.callback_query(lambda c: c.data == 'buy_photos')
async def buy_photos(callback_query: CallbackQuery):
    price = 45
    channel_name = "Photos"

    await save_link_request(callback_query.from_user.id, channel_name)

    # Обрабатываем покупку
    await process_purchase(callback_query, price)


@router.callback_query(lambda c: c.data == 'buy_videos_photos')
async def buy_videos_photos(callback_query: CallbackQuery):
    price = 90
    channel_name = "Videos + Photos"

    await save_link_request(callback_query.from_user.id, channel_name)

    await process_purchase(callback_query, price)



async def process_purchase(callback_query: CallbackQuery, price: int):
    telegram_id = callback_query.from_user.id

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()

    if not user:
        await callback_query.message.answer('❌ Ваш профиль не найден. Пожалуйста, зарегистрируйтесь.')
        conn.close()
        return

    user_coins = user[0]

    if user_coins >= price:
        new_balance = user_coins - price
        cursor.execute('UPDATE users SET balance = ? WHERE telegram_id = ?', (new_balance, telegram_id))
        conn.commit()

        await callback_query.message.answer("✅ Спасибо за запрос! Ожидайте, администратор свяжется с вами.")
    else:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(text='Пополнить', callback_data='replenish'))

        await callback_query.message.answer(
            f'🚫 Недостаточно 💎! Вам нужно ещё {price - user_coins} 💎. Чтобы пополнить баланс, нажмите кнопку:',
            reply_markup=kb.as_markup()
        )

    conn.close()