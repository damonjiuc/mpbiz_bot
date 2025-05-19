from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from services.manage_stores import orm_get_user_stores
from services.report_generator import get_weeks_range


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
        [InlineKeyboardButton(text='Канал с лайфхаками', url='https://t.me/khosnullin_channel'), InlineKeyboardButton(text='Поддержка', callback_data='cb_btn_help')],
        [InlineKeyboardButton(text='Профиль', callback_data='cb_btn_profile'), InlineKeyboardButton(text='Рефералы', callback_data='cb_btn_refs'), InlineKeyboardButton(text='Оплата', callback_data='cb_btn_payment')],
    ])

    return ikb

def get_subscribe_kb() -> InlineKeyboardMarkup:
    """Get subscribe kb"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подписаться на канал", url=f"https://t.me/khosnullin_channel")],
        [InlineKeyboardButton(text="Проверить подписку", callback_data="check_subscription")]
    ])

    return ikb


def get_contact_reply_kb() -> ReplyKeyboardMarkup:
    """Get contact reply kb"""
    rkb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отправить свой номер', request_contact=True),
            ],
        ],
    )

    return rkb


async def get_manage_kb(session, tg_id) -> InlineKeyboardMarkup:
    """Get manage stores kb"""
    ikb = InlineKeyboardBuilder()
    stores = await orm_get_user_stores(session=session, tg_id=tg_id)
    for store in stores:
        ikb.add(
            InlineKeyboardButton(text=f'Выбрать {store.name}', callback_data=f'setstore_{store.id}'),
            InlineKeyboardButton(text=f'Изменить {store.name}', callback_data=f'editstore_{store.id}'),
        )
    ikb.adjust(2)
    ikb.row(InlineKeyboardButton(text="Добавить магазин", callback_data='cb_btn_add_store'), )

    return ikb.as_markup()


def get_period_kb() -> InlineKeyboardMarkup:
    """Get select period kb"""
    ikb = InlineKeyboardBuilder()
    weeks_range = get_weeks_range(16)
    for week in weeks_range:
        ikb.add(
            InlineKeyboardButton(text=f'{week}', callback_data=f'setweek_{week}'),
        )
    ikb.adjust(1)

    return ikb.as_markup()


def get_payment_kb() -> InlineKeyboardMarkup:
    """Get payment kb"""
    ikb = InlineKeyboardBuilder()
    tariffs = {
        'test': {
            'name': 'Test',
            'price': 490.00,
            'generations_num': 1
        },
        'one': {
            'name': 'Разовый',
            'price': 490.00,
            'generations_num': 1
        },
        'month': {
            'name': 'Месяц',
            'price': 1690.00,
            'generations_num': 4
        },'quarter': {
            'name': 'Квартал',
            'price': 4990.00,
            'generations_num': 12
        },'year': {
            'name': 'Год',
            'price': 17990.00,
            'generations_num': 52
        },
    }
    for tariff in tariffs.values():
        ikb.add(
            InlineKeyboardButton(
                text=f'Оплатить {tariff["name"]}',
                callback_data=f'payfor_{tariff["generations_num"]}_{tariff["price"]}'
            )
        )
    ikb.adjust(1)
    ikb.row(InlineKeyboardButton(text="Меню", callback_data='cb_btn_menu'), )

    return ikb.as_markup()


def get_payment_check_kb(payment_id) -> InlineKeyboardMarkup:
    """Get kb for checking payment with input id"""
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Проверить оплату', callback_data=f'checkpayment_{payment_id}')],
        [InlineKeyboardButton(text="Выбрать другой тариф", callback_data="cb_btn_payment")]
    ])

    return ikb