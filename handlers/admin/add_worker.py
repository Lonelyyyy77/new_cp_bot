from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pyexpat.errors import messages

from database.admin.admin import add_worker_to_db
from states.admin.admin import AddWorker

router = Router()


@router.callback_query(lambda c: c.data == 'add_worker')
async def add_worker(callback: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Отменить', callback_data='cancel'))

    await callback.message.edit_text("Введите Telegram ID воркера:", reply_markup=kb.as_markup())
    await state.set_state(AddWorker.waiting_for_telegram_id)


@router.message(AddWorker.waiting_for_telegram_id)
async def process_telegram_id(message: Message, state: FSMContext):
    telegram_id = message.text.strip()

    if not telegram_id.isdigit():
        await message.answer("Пожалуйста, введите корректный Telegram ID (число). Попробуйте снова.")
        return

    await state.update_data(telegram_id=telegram_id)
    await message.answer("Теперь введите имя воркера:")

    await state.set_state(AddWorker.waiting_for_name)


@router.message(AddWorker.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    data = await state.get_data()
    telegram_id = data.get('telegram_id')

    add_worker_to_db(telegram_id, name)
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="К админке", callback_data='admin_panel'))

    await message.answer(f"Воркер {name} с Telegram ID {telegram_id} успешно добавлен!", reply_markup=kb.as_markup())

    await state.clear()


@router.callback_query(lambda c: c.data == 'cancel')
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await  callback.message.delete()
    await state.clear()
    await callback.message.answer("Процесс добавления воркера отменен.")
