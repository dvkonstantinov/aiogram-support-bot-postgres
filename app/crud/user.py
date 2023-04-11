from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import User


class CRUDUser(CRUDBase):
    async def get_user_by_telegram_id(
            self,
            telegram_id: int,
            session: AsyncSession
    ) -> Optional[User]:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()


crud_user = CRUDUser(User)
