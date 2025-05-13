import os
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Ref, User


async def generate_referral_link(user_id: int) -> str:
    return f"https://t.me/{os.getenv('BOT_USERNAME')}?start=ref_{user_id}"


async def orm_save_ref(session: AsyncSession, referrer_id: int, referral_id: int):
    query = select(Ref).where(Ref.referral_id == referral_id)
    result = await session.execute(query)
    if result.scalar_one_or_none() is None:
        obj = Ref(
            referrer_id=referrer_id,
            referral_id=referral_id,
        )
        session.add(obj)
        await session.commit()


async def orm_get_refs(session: AsyncSession, user_id: int) -> list[str]:
    query = (
        select(User.phone, User.first_name)
        .join(Ref, User.tg_id == Ref.referral_id)
        .where(Ref.referrer_id == user_id)
    )
    result = await session.execute(query)
    referrals = result.all()

    return [f"{phone} - {first_name}" for phone, first_name in referrals]