from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.user_keyboards import get_main_kb, get_menu_kb
from services.auth_service import orm_get_user
from services.refs import generate_referral_link, orm_get_refs

user_router = Router(name="user_router")


@user_router.message(or_f(Command("menu"), (F.text.lower().contains('меню')), (F.text.lower().contains('menu'))))
async def cmd_menu(msg: types.Message) -> None:
    """Command menu"""
    await handle_menu(msg)


@user_router.callback_query(F.data == 'cb_btn_menu')
async def cb_menu(callback: types.CallbackQuery) -> None:
    """Callback menu"""
    await handle_menu(callback.message)
    await callback.answer()


async def handle_menu(msg: types.Message) -> None:
    reply_text = 'МЕНЮ'
    await msg.answer(
        text=reply_text,
        reply_markup=get_menu_kb()
    )


@user_router.message(or_f(Command("about"), (F.text.lower().contains('о боте'))))
async def cmd_about(msg: types.Message) -> None:
    """Command about"""
    reply_text = 'Информация о том как работает бот'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.callback_query(F.data == 'cb_btn_news')
async def cb_news(callback: types.CallbackQuery) -> None:
    """Command news"""
    reply_text = 'Новости!'
    await callback.answer()
    await callback.message.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.message(or_f(Command("profile"), (F.text.lower().contains('профиль')), (F.text.lower().contains('кабинет'))))
async def cmd_profile(msg: types.Message) -> None:
    """Command profile"""
    await handle_profile(msg)


@user_router.callback_query(F.data == 'cb_btn_profile')
async def cb_profile(callback: types.CallbackQuery) -> None:
    """Callback profile"""
    await handle_profile(callback.message)
    await callback.answer()


async def handle_profile(msg: types.Message) -> None:
    reply_text = 'Профиль!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.callback_query(F.data == 'cb_btn_refs')
async def cb_refs(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Command refs"""
    user_id = int(callback.from_user.id)
    user = await orm_get_user(session, user_id)
    ref_link = await generate_referral_link(user_id)
    referrals = await orm_get_refs(session, user_id)
    reply_text = f'{callback.from_user.first_name}, ваша реферальная ссылка:\n'
    reply_text += f'{ref_link}\n\n'
    reply_text += f'Заработано бонусов: {user.bonus_total}\n'
    reply_text += f'Доступно для использования: {user.bonus_left}\n\n'
    reply_text += f'Список ваших рефералов:\n'
    for ref in referrals:
        reply_text += f'+{ref}\n'
    await callback.answer()
    await callback.message.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.callback_query(F.data == 'cb_btn_payment')
async def cb_payment(callback: types.CallbackQuery) -> None:
    """Command payment"""
    reply_text = 'Оплата!'
    await callback.answer()
    await callback.message.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.message(or_f(Command("help"), (F.text.lower().contains('помощь')), (F.text.lower().contains('поддержк')), (F.text.lower().contains('help'))))
async def cmd_help(msg: types.Message) -> None:
    """Command help"""
    await handle_help(msg)


@user_router.callback_query(F.data == 'cb_btn_help')
async def cb_help(callback: types.CallbackQuery) -> None:
    """Callback help"""
    await handle_help(callback.message)
    await callback.answer()


async def handle_help(msg: types.Message) -> None:
    reply_text = 'Поддержка!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.message(F.text)
async def cmd_any_text(msg: types.Message) -> None:
    """Command for any other text"""
    reply_text = 'Не знакомая команда\n'
    reply_text += 'Возможно Вы хотели вызвать меню'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )