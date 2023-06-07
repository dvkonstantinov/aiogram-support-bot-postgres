from datetime import datetime

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Message


class CRUDMessage(CRUDBase):
    async def get_by_date_interval(
            self,
            from_date: datetime,
            to_date: datetime,
            session: AsyncSession
    ):
        query = select(Message).where(and_(Message.created_at >= from_date,
                                           Message.created_at <= to_date))
        messages = await session.execute(query)
        messages = messages.scalars().all()
        return messages

    async def get_count_user_messages(
            self,
            telegram_id: int,
            session: AsyncSession
    ):
        stmt = select(func.count()).select_from(
            select(Message).where(Message.telegram_user_id == telegram_id)
        )
        mes_count = await session.execute(stmt)
        return mes_count.scalars().one()

    async def get_count_answers_to_user(
            self,
            telegram_id: int,
            session: AsyncSession
    ):
        stmt = select(func.count()).select_from(
            select(Message).where(Message.answer_to_user_id == telegram_id)
        )
        answers_count = await session.execute(stmt)
        return answers_count.scalars().one()


crud_message = CRUDMessage(Message)
