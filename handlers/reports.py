from datetime import datetime
from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth_service import orm_get_user
from keyboards.user_keyboards import get_period_kb, get_main_kb, get_manage_kb, get_menu_kb
from services.manage_stores import orm_add_store, orm_delete_store, orm_set_store
from services.payment import orm_reduce_generations
from services.report_generator import generate_report_with_params, run_with_progress, orm_add_report

reports_router = Router(name="reports_router")


# ------------------ Stores ------------------

class AddStore(StatesGroup):
    Name = State()
    Token = State()


@reports_router.message(or_f(Command("manage_stores"), (F.text.lower().contains('управлен')), (F.text.lower().contains('магазин'))))
async def cmd_manage_stores(msg: types.Message, session: AsyncSession) -> None:
    """Command manage_stores"""
    await handle_manage_stores(msg, msg.from_user.id, session)


@reports_router.callback_query(F.data == 'cb_btn_manage_stores')
async def cb_manage_stores(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Callback manage_stores"""
    await handle_manage_stores(callback.message, callback.from_user.id, session)
    await callback.answer()


async def handle_manage_stores(msg: types.Message, tg_id, session: AsyncSession) -> None:
    reply_text = 'Управление магазинами!'
    await msg.answer(
        text=reply_text,
        reply_markup=await get_manage_kb(session, tg_id)
    )

@reports_router.callback_query(F.data == 'cb_btn_add_store')
async def cb_add_store(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Callback add store"""
    reply_text = 'Введите название магазина:'
    await callback.message.answer(reply_text)
    await state.set_state(AddStore.Name)


@reports_router.message(AddStore.Name, F.text)
async def add_store_name(msg: types.Message, state: FSMContext):
    await state.update_data(tg_id=msg.from_user.id, name=msg.text)
    reply_text = 'Введите токен магазина Wildberries. При его создании необходимо выбрать доступ к следующим разделам:\n\n'
    reply_text += 'Контент, Статистика, Аналитика, Продвижение, Доступ чтение'
    await msg.answer(reply_text)
    await state.set_state(AddStore.Token)


@reports_router.message(AddStore.Token, F.text)
async def add_store_token(msg: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(token=msg.text)
    data = await state.get_data()
    reply_text = 'Магазин успешно добавлен!\n\n'
    reply_text += 'Можете переходить к генерации отчета!'
    await orm_add_store(session, data)
    await state.clear()
    await msg.answer(text=reply_text, reply_markup=get_menu_kb())


@reports_router.callback_query(F.data.startswith('deletestore_'))
async def cb_delete_store(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Callback delete store"""
    store_id = int(callback.data.split('_', 1)[1])

    await orm_delete_store(session, store_id)
    await callback.message.delete()
    reply_text = f'Магазин {store_id} удален'
    await callback.message.answer(reply_text)
    await callback.answer()

    await handle_manage_stores(callback.message, callback.from_user.id, session)


@reports_router.callback_query(F.data.startswith('setstore_'))
async def cb_set_store(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    """Callback set store"""
    store_id = int(callback.data.split('_', 1)[1])
    await orm_set_store(session, callback.from_user.id, store_id)
    reply_text = f'Магазин выбран, можете переходить к генерации отчета'
    await callback.message.answer(reply_text)
    await callback.answer()

    await handle_generate_report(callback.message, callback.from_user.id, session, state)


# ------------------ Reports ------------------

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
        await state.update_data(
            token=user.selected_store.token,
            name=user.selected_store.name,
            user_id=user.tg_id,
            store_id=user.selected_store.id,
        )
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
async def cmd_set_doc_num(msg: types.Message, state: FSMContext, session: AsyncSession):
    doc_num = msg.text
    await state.update_data(doc_num=doc_num)
    data = await state.get_data()
    reply_text = f'Номер(а) документа ({data["doc_num"]}) сохранен(ы).\nМагазин - {data["name"]}\nПериод - {data["period"]}'
    await msg.answer(reply_text)
    await state.clear()

    dates = data['period']
    doc_num = data['doc_num']
    store_name = data['name']
    store_token = data['token']
    tg_id = data['user_id']
    store_id = data['store_id']
    date = datetime.strptime(dates.split('-')[0], "%d.%m.%Y").date()

    try:
        file_path = await run_with_progress(
            msg,
            "Формируется отчет, пожалуйста, подождите",
            generate_report_with_params,
            dates, doc_num, store_token, store_name, tg_id, store_id
        )
        await msg.answer_document(FSInputFile(file_path))
        await orm_add_report(session, tg_id, date, file_path, store_id, store_name)
        await orm_reduce_generations(session, tg_id)
    except Exception as e:
        await msg.answer(
            text=f"Ошибка при формировании отчета:\n\n{e}",
            reply_markup=get_menu_kb()
        )
