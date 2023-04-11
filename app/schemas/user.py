from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBaseScheme(BaseModel):
    telegram_id: int
    telegram_username: Optional[str] = Field(None, max_length=100)
    is_banned: Optional[bool]
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_admin: Optional[bool] = Field(None)


class UserCreateScheme(UserBaseScheme):
    pass


class UserFormDBScheme(BaseModel):
    id: int
    is_banned: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
