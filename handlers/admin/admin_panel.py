from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.admin.admin import add_worker_to_db
from states.admin.admin import AddWorker

router = Router()


@router.callback_query(lambda c: c.data == 'admin_panel')
async def admin_panel_handler(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Добавить воркера', callback_data='add_worker'))
    kb.row(InlineKeyboardButton(text='Все воркеры', callback_data='view_workers'))
    kb.row(InlineKeyboardButton(text='Заявки на пополнение', callback_data='payment_req'))
    kb.row(InlineKeyboardButton(text='Пополнит счет', callback_data='replenish_user'))
    kb.row(InlineKeyboardButton(text='Посмотреть сообщения в поддержку', callback_data='view_support_messages'))

    await callback.message.edit_text('Вы успешно вошли в панель администратора.', reply_markup=kb.as_markup())


