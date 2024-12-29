from aiogram import Router
from aiogram.types import CallbackQuery

from database.worker.worker import get_referral_link

router = Router()


@router.callback_query(lambda c: c.data == 'referral_system')
async def referral_system(callback_query: CallbackQuery):
    telegram_id = callback_query.from_user.id

    referral_link = get_referral_link(telegram_id)

    if referral_link:
        await callback_query.message.answer(f"Ваша реферальная ссылка: {referral_link}")
    else:
        await callback_query.message.answer("Произошла ошибка при генерации вашей реферальной ссылки.")