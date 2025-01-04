import sqlite3

from aiogram import Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import TOKEN
from database import DB_NAME
from states.admin.admin import LinkRequest
import logging

router = Router()


@router.callback_query(lambda c: c.data == 'view_link_request')
async def view_link_requests(callback_query: CallbackQuery):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT id, telegram_id, channel_name FROM link_requests WHERE status = 'pending'")
    requests = cursor.fetchall()
    conn.close()

    if not requests:
        await callback_query.message.answer("🤷‍♂️ Нет новых запросов на ссылки.")
        return

    messages = []
    kb = InlineKeyboardBuilder()
    for request_id, telegram_id, channel_name in requests:
        messages.append(f"ID запроса: {request_id}\nTelegram ID: {telegram_id}\nКанал: {channel_name}")
        kb.row(InlineKeyboardButton(text=f"Ответить на {request_id}", callback_data=f"link_reply_{request_id}_{telegram_id}"))

    await callback_query.message.answer("\n\n".join(messages), reply_markup=kb.as_markup())


@router.callback_query(lambda c: c.data.startswith('link_reply_'))
async def reply_to_link_request(callback_query: CallbackQuery, state: FSMContext):
    try:
        logging.info(f"Received callback data: {callback_query.data}")

        # Разбираем callback_data для получения request_id и telegram_id
        parts = callback_query.data.split('_')

        # Логируем, что получилось после разбиения
        logging.info(f"Разделенные части: {parts}")

        if len(parts) != 4:
            await callback_query.answer("Ошибка: Неверный формат данных.")
            logging.error(
                f"Ошибка при разборе callback_data: {callback_query.data}. Ожидалось 4 части, но получено {len(parts)}.")
            return

        # Игнорируем первый элемент 'link' и берем нужные части
        _, _, request_id, telegram_id = parts

        # Проверяем на правильность данных
        request_id = int(request_id)
        telegram_id = int(telegram_id)

        # Сохраняем данные в состояние
        await state.update_data(request_id=request_id)
        await state.update_data(telegram_id=telegram_id)
        await state.set_state(LinkRequest.waiting_for_link)

        # Извлекаем имя пользователя из базы данных
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT username FROM users WHERE telegram_id = ?", (telegram_id,))
        user_data = cursor.fetchone()
        conn.close()

        # if user_data:
        #     username = user_data[0]
        #     # Сообщаем администратору, на какой ID отправляется ссылка
        #     await callback_query.message.answer(
        #         f"Вы собираетесь отправить ссылку пользователю с Telegram ID: {telegram_id} (username: {username}).")
        # else:
        #     # Если пользователя нет в базе данных
        #     await callback_query.message.answer(f"Пользователь с Telegram ID {telegram_id} не найден.")

        # Просим ввести ссылку
        await callback_query.message.answer("🔗 Введите ссылку для отправки пользователю.")

    except (IndexError, ValueError) as e:
        await callback_query.answer("Ошибка: Неверные данные для ответа.")
        # Логируем ошибку для отладки
        logging.error(f"Ошибка при разборе callback_data: {callback_query.data}, ошибка: {e}")



@router.message(LinkRequest.waiting_for_link)
async def handle_link_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    request_id = data.get("request_id")
    telegram_id = data.get("telegram_id")
    link = message.text

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT channel_name FROM link_requests WHERE id = ?", (request_id,))
    request_data = cursor.fetchone()

    if not request_data:
        await message.answer("Запрос не найден.")
        await state.clear()
        return

    channel_name = request_data[0]

    cursor.execute("UPDATE link_requests SET status = 'completed', admin_response = ? WHERE id = ?", (link, request_id))
    conn.commit()

    conn.close()

    bot = Bot(token=TOKEN)
    await bot.send_message(telegram_id, f"❤️ Ваша ссылка-приглашение:  {channel_name}: {link}")

    await message.answer(f"💌 Ссылка успешно отправлена пользователю с ID {telegram_id}.")
    await state.clear()