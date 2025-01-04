import sqlite3

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import DB_NAME
from database.worker.worker import get_all_workers, delete_worker

router = Router()


@router.callback_query(lambda call: call.data == 'view_workers')
async def view_workers_handler(callback: CallbackQuery, state: FSMContext):
    workers = get_all_workers()

    if not workers:
        back_kb = InlineKeyboardBuilder()
        back_kb.add(InlineKeyboardButton(text="К админ панели 🏡", callback_data="admin_panel"))

        await callback.message.edit_text("[🥷] Нет воркеров для отображения.", reply_markup=back_kb.as_markup())
        return

    page_size = 7
    total_pages = (len(workers) + page_size - 1) // page_size
    current_page = 0

    await state.update_data(current_page=current_page)

    await show_workers_page(callback, workers, current_page, page_size, total_pages)


async def show_workers_page(callback: CallbackQuery, workers, current_page, page_size, total_pages):
    start_index = current_page * page_size
    end_index = start_index + page_size
    workers_page = workers[start_index:end_index]

    workers_info = ""
    keyboard = InlineKeyboardBuilder()

    for worker in workers_page:
        worker_id, worker_name = worker

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('SELECT users_reffered, balance FROM workers WHERE telegram_id = ?', (worker_id,))
        worker_data = cursor.fetchone()

        if worker_data:
            users_referred, balance = worker_data
        else:
            users_referred, balance = 0, 0

        conn.close()

        workers_info += f"[🥷] ID: {worker_id}, Имя: {worker_name}, " \
                        f"Рефералов: {users_referred}, Баланс: {balance} монет\n\n"

        keyboard.row(InlineKeyboardButton(
            text=f"{worker_name} (Рефералов: {users_referred}, Баланс: {balance} монет)",
            callback_data=f"delete_worker_{worker_id}"
        ))

    keyboard.row(InlineKeyboardButton(text='К админ панели 🏡', callback_data='admin_panel'))

    navigation_buttons = []
    if current_page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"prev_page_{current_page - 1}"))
    if current_page < total_pages - 1:
        navigation_buttons.append(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"next_page_{current_page + 1}"))

    if navigation_buttons:
        keyboard.row(*navigation_buttons)

    await callback.message.edit_text(f"[🥷] Список воркеров:\n\n{workers_info}", reply_markup=keyboard.as_markup())
    await callback.answer()



@router.callback_query(lambda call: call.data.startswith('next_page_'))
async def next_page_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)

    workers = get_all_workers()
    page_size = 7
    total_pages = (len(workers) + page_size - 1) // page_size

    await state.update_data(current_page=current_page + 1)

    await show_workers_page(callback, workers, current_page + 1, page_size, total_pages)


@router.callback_query(lambda call: call.data.startswith('prev_page_'))
async def prev_page_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 0)

    workers = get_all_workers()
    page_size = 7
    total_pages = (len(workers) + page_size - 1) // page_size

    await state.update_data(current_page=current_page - 1)

    await show_workers_page(callback, workers, current_page - 1, page_size, total_pages)


@router.callback_query(lambda call: call.data.startswith('delete_worker_'))
async def delete_worker_handler(callback: CallbackQuery):
    worker_id = int(callback.data.split('_')[2])

    delete_worker(worker_id)

    workers = get_all_workers()
    page_size = 7
    total_pages = (len(workers) + page_size - 1) // page_size
    current_page = 0

    await show_workers_page(callback, workers, current_page, page_size, total_pages)

    await callback.answer()