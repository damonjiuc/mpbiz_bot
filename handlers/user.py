from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from tabulate import tabulate

from keyboards.user_keyboards import get_main_kb, get_payment_kb, get_payment_check_kb
from services.auth_service import orm_get_user
from services.payment import create_payment, check_payment, orm_check_payment_exists, orm_add_payment, \
    orm_add_generations
from services.refs import generate_referral_link, orm_get_refs, orm_get_referrer, orm_add_bonus

user_router = Router(name="user_router")


@user_router.message(or_f(Command("profile"), (F.text.lower().contains('профиль')), (F.text.lower().contains('кабинет'))))
async def cmd_profile(msg: types.Message, session: AsyncSession) -> None:
    """Command profile"""
    tg_id = msg.from_user.id
    await handle_profile(msg, tg_id, session)


@user_router.callback_query(F.data == 'cb_btn_profile')
async def cb_profile(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Callback profile"""
    tg_id = callback.from_user.id
    await handle_profile(callback.message, tg_id, session)
    await callback.answer()


async def handle_profile(msg: types.Message, tg_id:int, session: AsyncSession) -> None:
    user = await orm_get_user(session, tg_id)
    reply_text = 'Профиль!\n\n'
    reply_text += f'Генераций осталось: {user.generations_left}'
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
    reply_text = (
        '💳 <b>Тарифы и цены</b>\n\n'
        '📦 <b>Разовый</b>\n'
        '├─ 🔁 Генераций: 1\n'
        '├─ 💰 Цена: 490 ₽\n'
        '└─ 📊 За генерацию: 490 ₽\n\n'

        '📅 <b>Месяц</b>\n'
        '├─ 🔁 Генераций: 4\n'
        '├─ 💰 Цена: 1 690 ₽\n'
        '└─ 📊 За генерацию: 423 ₽\n\n'

        '🗓 <b>Квартал</b>\n'
        '├─ 🔁 Генераций: 12\n'
        '├─ 💰 Цена: 4 990 ₽\n'
        '└─ 📊 За генерацию: 416 ₽\n\n'

        '📆 <b>Год</b>\n'
        '├─ 🔁 Генераций: 52\n'
        '├─ 💰 Цена: 17 990 ₽\n'
        '└─ 📊 За генерацию: 346 ₽'
    )
    await callback.answer()
    await callback.message.answer(
        text=reply_text,
        reply_markup=get_payment_kb(),
        parse_mode='HTML'
    )


@user_router.callback_query(F.data.startswith('payfor_'))
async def cb_pay_for(callback: CallbackQuery):
    data = callback.data.split('_', 2)
    generations_num = data[1]
    amount = data[2]
    payment_url, payment_id = create_payment(callback.from_user.id, generations_num, amount)
    reply_text = 'Ваша ссылка на оплату:\n'
    reply_text += f'{payment_url}\n\n'
    reply_text += 'После того как проведете оплату нажмите на кнопку, чтобы проверить платеж'
    await callback.message.answer(
        text=reply_text,
        reply_markup=get_payment_check_kb(payment_id)
    )


@user_router.callback_query(F.data.startswith('checkpayment_'))
async def cb_check_payment(callback: CallbackQuery, session: AsyncSession):
    payment_id = callback.data.split('_', 1)[1]
    result = check_payment(payment_id)
    if await orm_check_payment_exists(session, payment_id):
        reply_text = 'Вы уже получили генерации за этот платеж'
    elif result:
        generations_num = int(result['generations_num'])
        tg_id = int(result['user_id'])
        amount = int(result['amount'])
        referrer = await orm_get_referrer(session, tg_id)
        if referrer is not None:
            await orm_add_bonus(session, referrer, amount)
        await orm_add_generations(session, tg_id, generations_num)
        await orm_add_payment(session, tg_id, amount, generations_num, payment_id)
        reply_text = f'Оплата прошла успешно, Вам добавлено {generations_num} генераций'
    else:
        reply_text = 'Платеж еще не прошел'
    await callback.message.answer(
        text=reply_text,
        reply_markup=get_main_kb()
    )