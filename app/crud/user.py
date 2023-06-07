import asyncio
from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import Message as TelegramMessage

from app.bot.utils import get_user_data
from app.crud.base import CRUDBase
from app.models import User
from app.schemas.user import UserBaseScheme


class CRUDUser(CRUDBase):
    async def get_user_by_telegram_id(
            self,
            telegram_id: int,
            session: AsyncSession
    ) -> Optional[User]:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()

    async def update(
            self,
            db_obj: User,
            obj_in: UserBaseScheme,
            session: AsyncSession
    ) -> User:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update_with_db_obj(
            self,
            updating_db_obj: User,
            session: AsyncSession
    ) -> User:
        session.add(updating_db_obj)
        await session.commit()
        await session.refresh(updating_db_obj)
        return updating_db_obj

    async def get_banned_users(
            self,
            session: AsyncSession
    ):
        banned_users = await session.execute(
            select(User).where(User.is_banned)
        )
        return banned_users.scalars().all()

    async def register_admin(self,
                             user: User,
                             session: AsyncSession) -> User:
        if user.is_admin:
            return user
        user.is_admin = True
        updated_user = await self.update_with_db_obj(user, session)
        return updated_user

    async def remove_admin(self,
                           user: User,
                           session: AsyncSession) -> User:
        if not user.is_admin:
            return user
        user.is_admin = False
        updated_user = await self.update_with_db_obj(user, session)
        return updated_user

    async def ban_user(self,
                       user: User,
                       session: AsyncSession) -> User:
        if user.is_banned:
            return user
        user.is_banned = True
        updated_user = await self.update_with_db_obj(user, session)
        return updated_user

    async def unban_user(self,
                         user: User,
                         session: AsyncSession) -> User:
        if not user.is_banned:
            return user
        user.is_banned = False
        updated_user = await self.update_with_db_obj(user, session)
        return updated_user

    async def get_or_create_user_by_tg_message(
            self,
            message: TelegramMessage,
            session: AsyncSession
    ) -> Optional[User]:
        telegram_id = message.from_user.id
        user = await self.get_user_by_telegram_id(telegram_id, session)
        if user:
            return user
        user_data = get_user_data(message)
        new_user = await self.create(user_data, session)
        return new_user


crud_user = CRUDUser(User)
