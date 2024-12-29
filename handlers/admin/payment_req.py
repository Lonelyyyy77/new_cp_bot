import sqlite3

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import DB_NAME
from database.admin.admin import get_all_replenishment_requests, get_all_replenishment_requests_start
from states.admin.admin import PaymentRequest

router = Router()


@router.callback_query(lambda c: c.data == 'payment_req')
async def payment_request(callback_query: CallbackQuery):
    requests = get_all_replenishment_requests_start()

    if not requests:
        await callback_query.answer("Нет заявок на пополнение.")
        return

    message_text = "Заявки на пополнение:\n\n"
    kb = InlineKeyboardBuilder()

    for request in requests:
        request_id, telegram_id, amount, _, worker_name = request
        message_text += f"ID заявки: {request_id}\n"
        message_text += f"ID пользователя: {telegram_id}\n"
        message_text += f"Сумма пополнения: {amount} монет\n"
        message_text += f"Реферер: {worker_name if worker_name else 'Не указан'}\n\n"

        kb.add(InlineKeyboardButton(
            text=f"Заявка ID {request_id}",
            callback_data=f"payment_{request_id}"
        ))

    kb.add(InlineKeyboardButton(text="Назад", callback_data="admin_panel"))
    await callback_query.message.edit_text(message_text, reply_markup=kb.as_markup())


@router.callback_query(lambda c: c.data.startswith('payment_'))
async def process_payment_request(callback_query: CallbackQuery, state: FSMContext):
    request_id = int(callback_query.data.split('_')[1])

    await state.update_data(request_id=request_id)

    await state.set_state(PaymentRequest.waiting_for_payment_details)
    await callback_query.message.answer("Введите реквизиты для оплаты:")
    await callback_query.answer()


@router.message(PaymentRequest.waiting_for_payment_details)
async def receive_payment_details(message: Message, state: FSMContext):
    payment_details = message.text

    data = await state.get_data()
    request_id = data.get("request_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT telegram_id FROM replenishment_requests WHERE id = ?", (request_id,))
    request_data = cursor.fetchone()

    if not request_data:
        await message.answer("Заявка не найдена.")
        await state.clear()
        return

    user_id = request_data[0]

    await message.bot.send_message(
        chat_id=user_id,
        text=f"Ваши реквизиты для оплаты:\n\n{payment_details}"
    )

    cursor.execute("UPDATE replenishment_requests SET status = 'processed' WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()

    await message.answer("Реквизиты отправлены пользователю, заявка обновлена.")
    await state.clear()