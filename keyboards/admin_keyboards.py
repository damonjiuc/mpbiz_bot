from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_admin_reply_kb() -> ReplyKeyboardMarkup:
    """Get admin reply kb"""
    rkb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Пользователи'),
                KeyboardButton(text='Новости'),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder='Введите команду'
    )

    return rkb