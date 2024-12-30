import logging
import sqlite3
from datetime import datetime

from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import TOKEN
from database import DB_NAME
from states.admin.admin import AdminSupportState

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@router.callback_query(lambda c: c.data == 'view_support_messages')
async def view_support_messages(callback_query: CallbackQuery):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        'SELECT id, user_id, telegram_id, message, created_at, status FROM support_messages WHERE status = "pending" ORDER BY created_at DESC')
    support_messages = cursor.fetchall()

    if not support_messages:
        await callback_query.message.answer("Нет сообщений от пользователей.")
        return

    messages_text = ""
    kb = InlineKeyboardBuilder()

    for msg in support_messages:
        message_id, user_id, telegram_id, support_message, created_at, status = msg
        messages_text += (
            f"Сообщение от пользователя с (ID: {telegram_id}):\n"
            f"Время: {created_at}\n"
            f"Сообщение: {support_message}\n\n"
        )
        kb.add(InlineKeyboardButton(text=f"Ответить пользователю {telegram_id}", callback_data=f"reply_{user_id}"))

    await callback_query.message.answer(
        messages_text,
        reply_markup=kb.as_markup()
    )

    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('reply_'))
async def reply_to_user(callback_query: CallbackQuery, state: FSMContext):
    logger.info(f"Received callback data: {callback_query.data}")

    try:
        user_telegram_id = int(callback_query.data.split('_')[1])
    except (IndexError, ValueError):
        await callback_query.answer("Ошибка: Неверные данные для ответа.")
        return

    await state.update_data(user_telegram_id=user_telegram_id)

    await callback_query.message.answer(
        "Введите ваш ответ для пользователя. Когда закончите, отправьте его."
    )

    await state.set_state(AdminSupportState.waiting_for_reply)


@router.message(AdminSupportState.waiting_for_reply)
async def handle_reply(message: Message, state: FSMContext):
    user_telegram_id = (await state.get_data()).get("user_telegram_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT telegram_id FROM support_messages WHERE telegram_id = ?", (user_telegram_id,))
    user_data = cursor.fetchone()

    if user_data:
        user_telegram_id = user_data[0]
        bot = Bot(token=TOKEN)

        try:
            if message.text:
                await bot.send_message(user_telegram_id, f"Ответ от администратора: {message.text}")
            elif message.photo:
                await bot.send_photo(user_telegram_id, photo=message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await bot.send_video(user_telegram_id, video=message.video.file_id, caption=message.caption)
            elif message.sticker:
                await bot.send_sticker(user_telegram_id, sticker=message.sticker.file_id)
            elif message.animation:
                await bot.send_animation(user_telegram_id, animation=message.animation.file_id, caption=message.caption)
            elif message.document:
                await bot.send_document(user_telegram_id, document=message.document.file_id, caption=message.caption)
            else:
                await message.answer("Этот тип сообщения не поддерживается для ответа пользователю.")
                return

            cursor.execute("UPDATE support_messages SET status = 'answered' WHERE telegram_id = ?", (user_telegram_id,))
            conn.commit()

            await message.answer("Ответ успешно отправлен пользователю!")
        except Exception as e:
            await message.answer(f"Ошибка при отправке ответа: {str(e)}")
    else:
        await message.answer("Пользователь не найден.")

    await state.clear()
