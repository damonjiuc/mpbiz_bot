from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


def get_main_kb() -> InlineKeyboardMarkup:
    """Get main kb"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Меню', callback_data='cb_btn_menu')]
    ])

    return ikb

def get_main_reply_kb() -> ReplyKeyboardMarkup:
    """Get main reply kb"""
    rkb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Меню'),
                KeyboardButton(text='О боте'),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder='Введите команду'
    )

    return rkb

def get_menu_kb() -> InlineKeyboardMarkup:
    """Get menu kb"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Генерация отчета', callback_data='cb_btn_generate_report'), InlineKeyboardButton(text='Управление магазинами', callback_data='cb_btn_manage_stores')],
        [InlineKeyboardButton(text='Новости', callback_data='cb_btn_news'), InlineKeyboardButton(text='Поддержка', callback_data='cb_btn_help')],
        [InlineKeyboardButton(text='Профиль', callback_data='cb_btn_profile'), InlineKeyboardButton(text='Рефералы', callback_data='cb_btn_refs'), InlineKeyboardButton(text='Оплата', callback_data='cb_btn_payment')],
    ])

    return ikb