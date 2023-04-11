from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import crud_user
from app.models import User
from app.schemas.user import UserCreateScheme


async def get_user_from_db(telegram_id: int,
                           session: AsyncSession) -> Optional[User]:
    user = await crud_user.get_user_by_telegram_id(telegram_id, session)
    return user


async def create_new_user(user_data: UserCreateScheme,
                          session: AsyncSession) -> User:
    new_user = await crud_user.create(user_data, session)
    return new_user
