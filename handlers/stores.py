from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy.ext.asyncio import AsyncSession

from handlers.reports import handle_generate_report
from services.manage_stores import orm_add_store, orm_delete_store, orm_set_store
from keyboards.user_keyboards import get_manage_kb, get_menu_kb

stores_router = Router(name="stores_router")


class AddStore(StatesGroup):
    Name = State()
    Token = State()


@stores_router.message(or_f(Command("manage_stores"), (F.text.lower().contains('управлен')), (F.text.lower().contains('магазин'))))
async def cmd_manage_stores(msg: types.Message, session: AsyncSession) -> None:
    """Command manage_stores"""
    await handle_manage_stores(msg, msg.from_user.id, session)


@stores_router.callback_query(F.data == 'cb_btn_manage_stores')
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

@stores_router.callback_query(F.data == 'cb_btn_add_store')
async def cb_add_store(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Callback add store"""
    reply_text = 'Введите название магазина:'
    await callback.message.answer(reply_text)
    await state.set_state(AddStore.Name)


@stores_router.message(AddStore.Name, F.text)
async def add_store_name(msg: types.Message, state: FSMContext):
    await state.update_data(tg_id=msg.from_user.id, name=msg.text)
    reply_text = 'Введите токен:\n'
    await msg.answer(reply_text)
    await state.set_state(AddStore.Token)


@stores_router.message(AddStore.Token, F.text)
async def add_store_token(msg: types.Message, state: FSMContext, session: AsyncSession):
    await state.update_data(token=msg.text)
    data = await state.get_data()
    reply_text = 'Магазин успешно добавлен:\n'
    reply_text += f'Название - {data["name"]}\n'
    reply_text += f'Токен - {data["token"]}\n\n'
    reply_text += 'Можете переходить к генерации отчета'
    await orm_add_store(session, data)
    await state.clear()
    await msg.answer(text=reply_text, reply_markup=get_menu_kb())


@stores_router.callback_query(F.data.startswith('deletestore_'))
async def cb_delete_store(callback: types.CallbackQuery, session: AsyncSession) -> None:
    """Callback delete store"""
    store_id = int(callback.data.split('_', 1)[1])

    await orm_delete_store(session, store_id)
    await callback.message.delete()
    reply_text = f'Магазин {store_id} удален'
    await callback.message.answer(reply_text)
    await callback.answer()

    await handle_manage_stores(callback.message, callback.from_user.id, session)


@stores_router.callback_query(F.data.startswith('setstore_'))
async def cb_set_store(callback: types.CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    """Callback set store"""
    store_id = int(callback.data.split('_', 1)[1])
    await orm_set_store(session, callback.from_user.id, store_id)
    reply_text = f'Магазин выбран, можете переходить к генерации отчета'
    await callback.message.answer(reply_text)
    await callback.answer()

    await handle_generate_report(callback.message, callback.from_user.id, session, state)