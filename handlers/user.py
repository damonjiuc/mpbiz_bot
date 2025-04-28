from aiogram import Router, types, F
from aiogram.filters import Command, or_f

from keyboards.user_keyboards import get_main_kb, get_menu_kb, get_main_reply_kb

user_router = Router(name="user_router")

@user_router.message(Command("start"))
async def cmd_start(msg: types.Message) -> None:
    """Command start"""
    reply_text = 'Бот запущен!\n'
    reply_text += f'Приветствую - {msg.from_user.first_name}!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_reply_kb()
    )

@user_router.message(Command("get_user_id"))
async def cmd_get_user_id(msg: types.Message) -> None:
    """Command get_user_id"""
    reply_text = f'Ваш id - {msg.from_user.id}!'
    print(msg.from_user)
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_reply_kb()
    )

@user_router.message(or_f(Command("menu"), (F.text.lower().contains('меню')), (F.text.lower().contains('menu'))))
async def cmd_menu(msg: types.Message) -> None:
    """Command menu"""
    reply_text = 'МЕНЮ'
    await msg.answer(
        text=reply_text,
        reply_markup=get_menu_kb()
    )

@user_router.message(or_f(Command("about"), (F.text.lower().contains('о боте'))))
async def cmd_menu(msg: types.Message) -> None:
    """Command about"""
    reply_text = 'Информация о том как работает бот'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("generate_report"), (F.text.lower().contains('отчет')), (F.text.lower().contains('отчёт'))))
async def cmd_generate_report(msg: types.Message) -> None:
    """Command generate_report"""
    reply_text = 'Создать отчёт!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("news"), (F.text.lower().contains('новости'))))
async def cmd_news(msg: types.Message) -> None:
    """Command news"""
    reply_text = 'Новости!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("manage_stores"), (F.text.lower().contains('управлен')), (F.text.lower().contains('магазин'))))
async def cmd_manage_stores(msg: types.Message) -> None:
    """Command manage_stores"""
    reply_text = 'Управление магазинами!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("profile"), (F.text.lower().contains('профиль')), (F.text.lower().contains('кабинет'))))
async def cmd_profile(msg: types.Message) -> None:
    """Command profile"""
    reply_text = 'Профиль!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("refs"), (F.text.lower().contains('реферал'))))
async def cmd_refs(msg: types.Message) -> None:
    """Command refs"""
    reply_text = 'Рефералы!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("payment"), (F.text.lower().contains('оплат'))))
async def cmd_payment(msg: types.Message) -> None:
    """Command payment"""
    reply_text = 'Оплата!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )

@user_router.message(or_f(Command("help"), (F.text.lower().contains('помощь')), (F.text.lower().contains('поддержк')), (F.text.lower().contains('help'))))
async def cmd_help(msg: types.Message) -> None:
    """Command help"""
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