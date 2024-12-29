import sqlite3

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import TOKEN
from database import DB_NAME
from database.admin.admin import get_all_replenishment_requests
from states.admin.admin import ReplenishUser

router = Router()


@router.callback_query(lambda c: c.data == 'replenish_user')
async def replenish_user(callback_query: CallbackQuery):
    requests = get_all_replenishment_requests(status="processed")

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
            text=f"Пополнить ID {request_id}",
            callback_data=f"replenish_{request_id}"
        ))

    kb.add(InlineKeyboardButton(text="Назад", callback_data="admin_panel"))
    await callback_query.message.edit_text(message_text, reply_markup=kb.as_markup())



@router.callback_query(lambda c: c.data.startswith('replenish_'))
async def process_replenish_request(callback_query: CallbackQuery, state: FSMContext):
    request_id = int(callback_query.data.split('_')[1])

    await state.update_data(request_id=request_id)

    await state.set_state(ReplenishUser.waiting_for_amount)

    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="100", callback_data="amount_100"))
    kb.add(InlineKeyboardButton(text="500", callback_data="amount_500"))
    kb.add(InlineKeyboardButton(text="1000", callback_data="amount_1000"))

    await callback_query.message.edit_text(
        "Выберите сумму пополнения:",
        reply_markup=kb.as_markup()
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data.startswith('amount_'))
async def confirm_replenishment(callback_query: CallbackQuery, state: FSMContext):
    amount = int(callback_query.data.split('_')[1])

    data = await state.get_data()
    request_id = data.get("request_id")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT telegram_id, worker_name FROM replenishment_requests WHERE id = ?", (request_id,))
    request_data = cursor.fetchone()

    if not request_data:
        await callback_query.message.edit_text("Заявка не найдена.")
        await state.clear()
        return

    telegram_id, worker_name = request_data

    cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    user_data = cursor.fetchone()
    user_balance = user_data[0] if user_data else 0
    new_balance = user_balance + amount

    cursor.execute("UPDATE users SET balance = ? WHERE telegram_id = ?", (new_balance, telegram_id))

    bot = Bot(token=TOKEN)
    await bot.send_message(telegram_id, f"Ваш баланс был пополнен на {amount} монет. Новый баланс: {new_balance} монет.")

    if worker_name:
        cursor.execute("SELECT telegram_id, balance FROM workers WHERE name = ?", (worker_name,))
        worker_data = cursor.fetchone()
        if worker_data:
            worker_id, worker_balance = worker_data
            referral_bonus = int(amount * 0.1)
            new_worker_balance = worker_balance + referral_bonus
            cursor.execute("UPDATE workers SET balance = ? WHERE telegram_id = ?", (new_worker_balance, worker_id))

    cursor.execute("UPDATE replenishment_requests SET status = 'replenished' WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()

    await callback_query.message.edit_text(
        f"Пользователю ID {telegram_id} начислено {amount} монет. Заявка обновлена."
    )
    await callback_query.answer()
    await state.clear()
