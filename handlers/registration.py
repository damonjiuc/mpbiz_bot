from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.user_keyboards import get_menu_kb, get_subscribe_kb, get_after_reg_kb, \
    get_contact_reply_kb
from services import auth_service
from services.refs import orm_save_ref

registration_router = Router(name="registration_router")


class Registration(StatesGroup):
    contact = State()


@registration_router.message(Command("start"))
async def cmd_start(msg: types.Message, state: FSMContext, session: AsyncSession) -> None:
    """Command start"""
    await state.clear()
    user_id = int(msg.from_user.id)
    is_registered = await auth_service.orm_check_user_reg(session, user_id)
    member = await msg.bot.get_chat_member('@khosnullin_channel', user_id) #@khosnullin_channel

    if len(msg.text.split()) > 1:
        args = msg.text.split()[1]
        if args.startswith('ref_'):
            referrer_id = int(args.split('_')[1])
            print(referrer_id)
            if referrer_id != msg.from_user.id:
                await orm_save_ref(session, referrer_id, msg.from_user.id)

    if is_registered:
        reply_text = f'Приветствую - {msg.from_user.first_name}!\n'
        reply_text += 'Меню:'
        await msg.answer(
            text=reply_text,
            reply_markup=get_menu_kb()
        )
    elif member.status not in ["member", "administrator", "creator"]:
        reply_text = f'Приветствую - {msg.from_user.first_name}!\n'
        reply_text += 'Для доступа к боту подпишитесь на канал @khosnullin_channel!' #@khosnullin_channel
        await msg.answer(
            text=reply_text,
            reply_markup=get_subscribe_kb()
        )
    else:
        await state.set_state(Registration.contact)
        await msg.answer("Пожалуйста, поделитесь своим контактом.", reply_markup=get_contact_reply_kb())


@registration_router.callback_query(F.data == 'check_subscription')
async def check_subscription(callback: types.CallbackQuery, state: FSMContext):
    member = await callback.bot.get_chat_member('@mp_bot_test', callback.from_user.id) #@khosnullin_channel
    if member.status not in ["member", "administrator", "creator"]:
        await callback.answer("Вы ещё не подписаны.", show_alert=True)
    else:
        await state.set_state(Registration.contact)
        await callback.message.answer("Пожалуйста, поделитесь своим контактом.", reply_markup=get_contact_reply_kb())


@registration_router.message(Registration.contact, F.contact)
async def add_user(msg: types.Message, state: FSMContext, session: AsyncSession):
    user_data = {
        'tg_id': msg.from_user.id,
        'phone': msg.contact.phone_number.lstrip('+'),
        'first_name': msg.from_user.first_name,
        'user_name': msg.from_user.username
    }
    await auth_service.orm_add_user(session, user_data)
    await state.clear()
    await msg.bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id-1)
    reply_text = 'Вы успешно зарегистрированы!\n'
    reply_text += 'Для перехода к управлению магазинами нажмите на кнопку'

    await msg.answer(
        text=reply_text,
        reply_markup=get_after_reg_kb()
    )