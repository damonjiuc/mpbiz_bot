import yookassa
import uuid
import os

from sqlalchemy import update, select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Payment


yookassa.Configuration.configure(f'{os.getenv("UKASSA_ACCOUNT_ID")}', f'{os.getenv("UKASSA_SECRET_KEY")}')


async def orm_reduce_generations(session: AsyncSession, tg_id:int):
    query = update(User).where(User.tg_id == tg_id).values(generations_left=User.generations_left - 1)
    await session.execute(query)
    await session.commit()


def create_payment(tg_id, generations_num, amount):
    id_key = str(uuid.uuid4())
    return_url = f'https://t.me/{os.getenv("BOT_USERNAME")}'
    payment = yookassa.Payment.create(
    {
        'amount': {
            'value': amount,
            'currency': "RUB"
        },
        'confirmation': {
            'type': 'redirect',
            'return_url': return_url
        },
        'capture': True,
        'description': 'Оплата генераций отчетов в боте Paganini',
        'metadata': {
            'user_id': tg_id,
            'generations_num': generations_num,
            'amount': int(float(amount))
        }
    }, id_key)

    return payment.confirmation.confirmation_url, payment.id


def check_payment(payment_id):
    payment = yookassa.Payment.find_one(payment_id)
    if payment.status == 'succeeded':
        return payment.metadata
    else:
        return False


async def orm_check_payment_exists(session: AsyncSession, yoo_id: str) -> bool:
    query = select(exists().where(Payment.yoo_id == yoo_id))
    result = await session.execute(query)
    return result.scalar()


async def orm_add_generations(session: AsyncSession, tg_id: int, generations_num: int):
    query = update(User).where(User.tg_id == tg_id).values(generations_left=User.generations_left + generations_num)
    await session.execute(query)
    await session.commit()


async def orm_add_payment(session: AsyncSession, tg_id: int, amount: int, generations_num: int, yoo_id: str):
    obj = Payment(
        tg_id=tg_id,
        amount=amount,
        generations_num=generations_num,
        yoo_id=yoo_id
    )
    session.add(obj)
    await session.commit()