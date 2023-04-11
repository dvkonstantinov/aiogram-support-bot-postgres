from datetime import datetime
from typing import List

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Message, User


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


crud_message = CRUDMessage(Message)
