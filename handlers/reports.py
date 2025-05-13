from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.stores import handle_manage_stores
from services.auth_service import orm_get_user
from keyboards.user_keyboards import get_period_kb, get_main_kb

reports_router = Router(name="reports_router")


class Report(StatesGroup):
    Period = State()
    Doc_num = State()


@reports_router.message(or_f(Command("generate_report"), (F.text.lower().contains('отчет')), (F.text.lower().contains('отчёт'))))
async def cmd_generate_report(msg: types.Message, session: AsyncSession, state: FSMContext) -> None:
    """Command generate_report"""
    await handle_generate_report(msg, msg.from_user.id, session, state)


@reports_router.callback_query(F.data == 'cb_btn_generate_report')
async def cb_generate_report(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    """Callback generate_report"""
    await handle_generate_report(callback.message, callback.from_user.id, session, state)
    await callback.answer()


async def handle_generate_report(msg: types.Message, tg_id, session: AsyncSession, state: FSMContext) -> None:
    user = await orm_get_user(session, tg_id)
    if user.generations_left <= 0 and user.role not in {'admin', 'whitelist'}:
        reply_text = f'{user.first_name}, у Вас кончились генерации отчетов, оплатите бота'
        await msg.answer(
            text=reply_text,
            reply_markup=get_main_kb()
        )
    elif user.selected_store_id:
        reply_text = f'{user.first_name}, для генерации отчета у Вас выбран магазин {user.selected_store.name}\n'
        reply_text += 'Для изменения магазина перейдите в управление магазинами\n\n'
        reply_text += f'Осталось генераций: {user.generations_left}\n\n'
        reply_text += 'Чтобы создать отчет - выберите период за который его нужно сгенерировать'
        await msg.answer(
            text=reply_text,
            reply_markup=get_period_kb()
        )
        await state.set_state(Report.Period)
        await state.update_data(token=user.selected_store.token)
    else:
        reply_text = 'У вас не выбран магазин для генерации отчета\n'
        reply_text += 'Выберите текущий, или создайте новый'
        await msg.answer(
            text=reply_text
        )

        await handle_manage_stores(msg, tg_id, session)


@reports_router.callback_query(Report.Period, F.data.startswith('setweek_'))
async def cb_set_period(callback: CallbackQuery, state: FSMContext):
    period = callback.data.split('_', 1)[1]
    await state.update_data(period=period)
    reply_text = 'Пожалуйста, введите номер документа!\n\n'
    reply_text += 'Чтобы его получить в личном кабинете WB зайдите в Финансовые отчеты, в колонке Прочие удержания нажмите на сумму, Вам нужен номер документа с комментарием Оказание услуг «ВБ.Продвижение»\n\n'
    reply_text += 'Если у Вас такого нету введите 123, если у Вас 2 номера документа - введите их через пробел, например «232411108 233498006»'
    await callback.message.answer(reply_text)
    await state.set_state(Report.Doc_num)


@reports_router.message(Report.Doc_num, F.text)
async def cmd_set_doc_num(msg: types.Message, state: FSMContext):
    doc_num = msg.text
    await state.update_data(doc_num=doc_num)
    data = await state.get_data()
    reply_text = f'Номер(а) документа ({data["doc_num"]}) сохранен(ы).\nОжидайте формирования отчета...\n'
    reply_text += f'Токен - {data["token"]}\t Период - {data["period"]}'
    await msg.answer(reply_text)
    await state.clear()

