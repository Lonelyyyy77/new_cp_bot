import sqlite3

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from database import DB_NAME
from states.user.user import SupportState

router = Router()


@router.callback_query(lambda c: c.data == 'help')
async def show_help(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(SupportState.waiting_for_message)

    await callback_query.message.answer(
        "Пожалуйста, введите ваше сообщение для техподдержки."
    )


@router.message(SupportState.waiting_for_message)
async def process_support_message(message: Message, state: FSMContext):
    user_id = message.from_user.id
    telegram_id = message.from_user.id
    support_message = message.text

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO support_messages (user_id, telegram_id, message)
        VALUES (?, ?, ?)
    ''', (user_id, telegram_id, support_message))

    conn.commit()
    conn.close()

    await message.answer("Ваше сообщение отправлено в техподдержку. Мы скоро с вами свяжемся.")

    await state.clear()
