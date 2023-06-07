from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MessageBaseScheme(BaseModel):
    telegram_user_id: int
    text: Optional[str]
    attachments: Optional[bool]
    answer_to_user: Optional[int]


class MessageCreateScheme(MessageBaseScheme):
    pass


class MessageFromDBScheme(MessageBaseScheme):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
