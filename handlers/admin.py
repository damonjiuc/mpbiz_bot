from aiogram import Router, types, F
from aiogram.filters import Command, or_f

from filters.chat_types import ChatTypeFilter, IsAdmin
from keyboards.admin_keyboards import get_admin_reply_kb

admin_router = Router(name="admin_router")
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdmin())

@admin_router.message(or_f(Command("admin"), (F.text.lower().contains('админ')), (F.text.lower().contains('admin'))))
async def cmd_admin(msg: types.Message) -> None:
    """Command admin"""
    reply_text = f'Приветствую - {msg.from_user.first_name}!\n'
    reply_text += f'Вы в админ панели'
    await msg.answer(
        text=reply_text,
        reply_markup=get_admin_reply_kb()
    )