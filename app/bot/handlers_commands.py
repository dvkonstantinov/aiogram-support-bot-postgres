from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject
from aiogram.exceptions import TelegramAPIError
from aiogram.types import Message

from app.bot.get_reports import get_month_report
from app.bot.utils import get_user_name, extract_user_id
from app.core.config import settings
from app.core.db import get_async_session
from app.crud.user import crud_user
from app.services.user import get_user_from_db

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message) -> None:
    print(message.from_user)
    user_data = {
        'telegram_id': message.from_user.id,
        'telegram_username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
    }
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    existing_user = await get_user_from_db(
        message.from_user.id, session
    )
    if not existing_user:
        await crud_user.create(user_data, session)
    if existing_user and existing_user.is_banned:
        return
    await message.answer(
        "Привет! Мы - команда поддержки. Если у вас есть вопрос, "
        "напишите нам, мы с радостью на него ответим.\n"
        "Мы работаем по будням с 9:00 до 18:00, но можем ответить и в другое "
        "время, если не будем заняты:)",
    )


@router.message(Command(commands="info"),
                F.chat.id == int(settings.GROUP_ID),
                F.reply_to_message)
async def get_user_info(message: Message, bot: Bot):
    try:
        user_id = extract_user_id(message.reply_to_message)
    except ValueError as err:
        return await message.reply(str(err))

    try:
        user = await bot.get_chat(user_id)
    except TelegramAPIError as err:
        await message.reply(
            text=(f'Невозможно найти пользователя с таким Id. Текст ошибки:\n'
                  f'{err.message}')
        )
        return

    username = f"@{user.username}" if user.username else "отсутствует"
    await message.reply(text=f'Имя: {get_user_name(user)}\n'
                             f'Id: {user.id}\n'
                             f'username: {username}')


@router.message(Command(commands='report'),
                F.chat.id == int(settings.GROUP_ID))
async def get_report(message: Message,
                     bot: Bot,
                     command: CommandObject):
    args = command.args
    print(args)
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    report = await get_month_report(
        session)

    answer_text = (f"Отчет за месяц, c {report['from_date']} до "
                   f"{report['to_date']}.\n"
                   f"Всего было получено {report['questions_amount']} "
                   f"сообщений от {report['users_amount']} клиентов.\n"
                   f"Количество ответов от администраторов: {report['answers_amount']}")
    await bot.send_message(chat_id=int(settings.GROUP_ID), text=answer_text)

