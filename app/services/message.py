from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.message import crud_message
from app.models import Message
from app.schemas.message import MessageCreateScheme


async def create_new_message(message_data: MessageCreateScheme,
                             session: AsyncSession) -> Message:
    new_message = await crud_message.create(message_data, session)
    return new_message
