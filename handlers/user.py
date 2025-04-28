from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.user_keyboards import get_main_kb, get_menu_kb, get_main_reply_kb, get_subscribe_kb, \
    get_contact_reply_kb, get_after_reg_kb
from services import auth_service

user_router = Router(name="user_router")


class Registration(StatesGroup):
    contact = State()


@user_router.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """Command start"""
    await state.clear()
    user_id = int(msg.from_user.id)
    is_registered = await auth_service.orm_check_user_reg(session, user_id)
    member = await msg.bot.get_chat_member('@mp_bot_test', user_id) #@khosnullin_channel
    if is_registered:
        reply_text = f'Приветствую - {msg.from_user.first_name}!\n'
        reply_text += 'Меню:'
        await msg.answer(
            text=reply_text,
            reply_markup=get_menu_kb()
        )
    elif member.status not in ["member", "administrator", "creator"]:
        reply_text = f'Приветствую - {msg.from_user.first_name}!\n'
        reply_text += 'Для доступа к боту подпишитесь на канал @mp_bot_test!' #@khosnullin_channel
        await msg.answer(
            text=reply_text,
            reply_markup=get_subscribe_kb()
        )
    else:
        await state.set_state(Registration.contact)
        await msg.answer("Пожалуйста, поделитесь своим контактом.", reply_markup=get_contact_reply_kb())


@user_router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: types.CallbackQuery, state: FSMContext):
    member = await callback.bot.get_chat_member('@mp_bot_test', callback.from_user.id) #@khosnullin_channel
    if member.status not in ["member", "administrator", "creator"]:
        await callback.answer("Вы ещё не подписаны.", show_alert=True)
    else:
        await state.set_state(Registration.contact)
        await callback.message.answer("Пожалуйста, поделитесь своим контактом.", reply_markup=get_contact_reply_kb())


@user_router.message(Registration.contact, F.contact)
async def add_user(msg: types.Message, state: FSMContext, session: AsyncSession):
    user_data = {
        'tg_id': msg.from_user.id,
        'phone': msg.contact.phone_number.lstrip('+'),
        'first_name': msg.from_user.first_name,
        'user_name': msg.from_user.username
    }
    await auth_service.orm_add_user(session, user_data)
    reply_text = 'Вы успешно зарегистрированы!\n'
    reply_text += 'Для перехода к управлению магазинами нажмите на кнопку'
    await msg.answer(
        text=reply_text,
        reply_markup=get_after_reg_kb()
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


@user_router.message(or_f(Command("generate_report"), (F.text.lower().contains('отчет')), (F.text.lower().contains('отчёт'))))
async def cmd_generate_report(msg: types.Message) -> None:
    """Command generate_report"""
    await handle_generate_report(msg)


@user_router.callback_query(F.data == 'cb_btn_generate_report')
async def cb_generate_report(callback: types.CallbackQuery) -> None:
    """Callback generate_report"""
    await handle_generate_report(callback.message)
    await callback.answer()


async def handle_generate_report(msg: types.Message) -> None:
    reply_text = 'Создать отчёт!'
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


@user_router.message(or_f(Command("manage_stores"), (F.text.lower().contains('управлен')), (F.text.lower().contains('магазин'))))
async def cmd_manage_stores(msg: types.Message) -> None:
    """Command manage_stores"""
    await handle_manage_stores(msg)


@user_router.callback_query(F.data == 'cb_btn_manage_stores')
async def cb_manage_stores(callback: types.CallbackQuery) -> None:
    """Callback manage_stores"""
    await handle_manage_stores(callback.message)
    await callback.answer()


async def handle_manage_stores(msg: types.Message) -> None:
    reply_text = 'Управление магазинами!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.message(or_f(Command("profile"), (F.text.lower().contains('профиль')), (F.text.lower().contains('кабинет'))))
async def cmd_profile(msg: types.Message) -> None:
    """Command profile"""
    await handle_profile(msg)


@user_router.callback_query(F.data == 'cb_btn_profile')
async def cb_profile(callback: types.CallbackQuery) -> None:
    """Callback manage_stores"""
    await handle_profile(callback.message)
    await callback.answer()


async def handle_profile(msg: types.Message) -> None:
    reply_text = 'Профиль!'
    await msg.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )


@user_router.callback_query(F.data == 'cb_btn_refs')
async def cb_refs(callback: types.CallbackQuery) -> None:
    """Command refs"""
    reply_text = 'Рефералы!'
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