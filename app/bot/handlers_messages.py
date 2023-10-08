from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import Message

from app.bot.utils import extract_user_id, check_user_is_banned
from app.core.config import settings
from app.core.db import get_async_session
from app.crud.message import crud_message
from app.crud.user import crud_user
from filter_media import SupportedMediaFilter

router = Router()


@router.message(F.chat.type == 'private', F.text)
async def send_message_to_group(message: Message, bot: Bot):
    if message.text and len(message.text) > 4000:
        return await message.reply(text='Пожалуйста, уменьшите размер '
                                        'сообщения, чтобы оно было менее '
                                        '4000 символов')
    await bot.send_message(
        chat_id=settings.GROUP_ID,
        text=(
            f'{message.text}\n\n'
            f'Тикет: #id{message.from_user.id}'
        ),
        parse_mode='HTML'
    )
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    db_user = await crud_user.get_or_create_user_by_tg_message(message, session)
    if check_user_is_banned(db_user):
        return
    message_data = {
        'text': message.text,
        'telegram_user_id': message.from_user.id,
        'attachments': False,
    }

    await crud_message.create(message_data, session)


@router.message(SupportedMediaFilter(), F.chat.type == 'private')
async def supported_media(message: Message):
    if message.caption and len(message.caption) > 1000:
        return await message.reply(text='Слишком длинное описание. Описание '
                                        'не может быть больше 1000 символов')
    await message.copy_to(
        chat_id=settings.GROUP_ID,
        caption=((message.caption or "") +
                 f"\n\n Тикет: #id{message.from_user.id}"),
        parse_mode="HTML"
    )
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    db_user = await crud_user.get_or_create_user_by_tg_message(message, session)
    if check_user_is_banned(db_user):
        return
    message_data = {
        'telegram_user_id': message.from_user.id,
        'attachments': True,
    }
    if message.caption:
        message_data['text'] = message.caption
    await crud_message.create(message_data, session)


@router.message(F.chat.id == int(settings.GROUP_ID),
                F.reply_to_message)
async def send_message_answer(message: Message,
                              bot: Bot):
    if not message.reply_to_message.from_user.is_bot:
        return
    try:
        chat_id = extract_user_id(message.reply_to_message)
    except ValueError as err:
        return await message.reply(text=f'Не могу извлечь Id.  Возможно он '
                                        f'некорректный. Текст ошибки:\n'
                                        f'{str(err)}')
    try:
        await message.copy_to(chat_id)
    except TelegramForbiddenError:
        await message.reply(text='Сообщение не доставлено. Бот был '
                                 'заблокировн пользователем, '
                                 'либо пользователь удален')
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    db_user = await crud_user.get_or_create_user_by_tg_message(message, session)
    await crud_user.register_admin(db_user, session)
    message_data = {
        'telegram_user_id': message.from_user.id,
        'answer_to_user_id': chat_id,
    }
    if message.text:
        message_data['text'] = message.text
    else:
        if message.caption:
            message_data['text'] = message.caption
            message_data['attachments'] = True

    await crud_message.create(message_data, session)
