from aiogram.fsm.state import State, StatesGroup


class AddWorker(StatesGroup):
    waiting_for_telegram_id = State()
    waiting_for_name = State()


class PaymentRequest(StatesGroup):
    waiting_for_payment_details = State()


class ReplenishUser(StatesGroup):
    waiting_for_amount = State()


class AdminSupportState(StatesGroup):
    waiting_for_reply = State()