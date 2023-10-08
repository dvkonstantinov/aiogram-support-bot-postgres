from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.bot.get_reports import get_report_from_db
from app.bot.utils import get_user_name, check_input_date_correct, \
    stringdate_to_date, check_user_is_banned, \
    get_telegram_user_from_resend_message, parse_ban_command
from app.core.config import settings
from app.core.db import get_async_session
from app.crud.user import crud_user
from app.crud.message import crud_message

router = Router()


@router.message(Command(commands=["start"]))
async def command_start(message: Message):
    await message.answer(settings.START_MESSAGE)
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    db_user = await crud_user.get_or_create_user_by_tg_message(message,
                                                               session)
    if check_user_is_banned(db_user):
        return


@router.message(Command(commands="info"),
                F.chat.id == int(settings.GROUP_ID),
                F.reply_to_message)
async def get_user_info(message: Message, bot: Bot):
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    telegram_user = await get_telegram_user_from_resend_message(message, bot)
    if not telegram_user:
        return
    messages_count = await crud_message.get_count_user_messages(
        telegram_user.id, session
    )
    ans_count = await crud_message.get_count_answers_to_user(
        telegram_user.id, session
    )
    username = f"@{telegram_user.username}" if telegram_user.username else "отсутствует"
    await message.reply(text=f'Имя: {get_user_name(telegram_user)}\n'
                             f'Id: {telegram_user.id}\n'
                             f'username: {username}\n'
                             f'Сообщений от пользователя: {messages_count}\n'
                             f'Ответов пользователю: {ans_count}\n')


@router.message(Command(commands='report'),
                F.chat.id == int(settings.GROUP_ID))
async def get_report(message: Message,
                     bot: Bot,
                     command: CommandObject):
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    if command.args:
        if not check_input_date_correct(command.args):
            answer_text = 'Неверный формат даты'
            await bot.send_message(
                chat_id=int(settings.GROUP_ID), text=answer_text
            )
            return
        from_date, to_date = stringdate_to_date(command.args)
        report = await get_report_from_db(session, from_date, to_date)
        report['period'] = 'выбранный период'
    else:
        report = await get_report_from_db(session)
        report['period'] = 'последний месяц'

    answer_text = (f"Отчет за {report['period']}, c {report['from_date']} до "
                   f"{report['to_date']}.\n"
                   f"Всего было получено {report['questions_amount']} "
                   f"сообщений от {report['users_amount']} клиентов.\n"
                   f"Количество ответов от администраторов: {report['answers_amount']}")
    await bot.send_message(chat_id=int(settings.GROUP_ID), text=answer_text)


@router.message(Command(commands='ban'),
                F.chat.id == int(settings.GROUP_ID))
async def handler_ban_user(message: Message,
                           bot: Bot,
                           command: CommandObject):
    if not command.args and not message.reply_to_message:
        return await message.reply(
            text='Команда некорректна. Укажите ID или ответьте на сообщение')
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    if command.args:
        telegram_user_id = parse_ban_command(command)
        if not telegram_user_id:
            return await message.reply(
                text='Невозможно извлечь id пользователя. '
                     'Нужно ввести id в формате "12345", либо ответить на '
                     'сообщение пользователя, которого хотите забанить')
        try:
            telegram_user = await bot.get_chat(telegram_user_id)
        except TelegramBadRequest:
            return await message.reply(
                text='Пользователя с таким id не существует ')

    else:
        telegram_user = await get_telegram_user_from_resend_message(message, bot)
        if not telegram_user:
            return
    db_user = await crud_user.get_user_by_telegram_id(telegram_user.id,
                                                      session)
    await crud_user.ban_user(db_user, session)
    await message.reply(text=f'Пользователь {db_user.first_name} '
                             f'{db_user.last_name} забанен.'
                             f'Чтобы разбанить, отправьте /unban\n'
                             f'Тикет: #id{db_user.telegram_id}')


@router.message(Command(commands='unban'),
                F.chat.id == int(settings.GROUP_ID))
async def handler_unban_user(message: Message,
                             bot: Bot,
                             command: CommandObject):
    if not command.args and not message.reply_to_message:
        return await message.reply(
            text='Команда некорректна. Укажите ID или ответьте на сообщение')
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    if command.args:
        telegram_user_id = parse_ban_command(command)
        if not telegram_user_id:
            return await message.reply(
                text='Невозможно извлечь id пользователя. '
                     'Нужно ввести id в формате "12345", либо ответить на '
                     'сообщение пользователя, которого хотите забанить')
        db_user = await crud_user.get_user_by_telegram_id(telegram_user_id,
                                                          session)
    else:
        telegram_user = await get_telegram_user_from_resend_message(message, bot)
        if not telegram_user:
            return
        db_user = await crud_user.get_user_by_telegram_id(telegram_user.id,
                                                          session)
    await crud_user.unban_user(db_user, session)
    await message.reply(text=f'Пользователь с id '
                             f'{db_user.first_name} {db_user.last_name} разбанен\n'
                             f'Тикет: #id{db_user.telegram_id}')


@router.message(Command(commands='banlist'),
                F.chat.id == int(settings.GROUP_ID))
async def handler_unban_user(message: Message,
                             bot: Bot):
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    banned_users = await crud_user.get_banned_users(session)
    text = 'Список забанненых пользователей:\n'
    for user in banned_users:
        text += f'{user.telegram_id} - {user.first_name} {user.last_name}\n'
    await message.reply(text=text)


@router.message(Command(commands='registeradmin'),
                F.chat.id == int(settings.GROUP_ID))
async def handle_register_admin(message: Message,
                                bot: Bot):
    if not message.reply_to_message:
        return message.reply(text="Введите команду как ответ на сообщение "
                                  "пользователя")
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    db_user = await crud_user.get_or_create_user_by_tg_message(
        message.reply_to_message,
        session
    )
    db_user = await crud_user.register_admin(db_user, session)
    text = (f'Пользователь {db_user.first_name} {db_user.last_name} теперь '
            f'администратор')
    await message.reply(text=text)


@router.message(Command(commands='deleteadmin'),
                F.chat.id == int(settings.GROUP_ID))
async def handle_remove_admin(message: Message,
                              bot: Bot):
    if not message.reply_to_message:
        return message.reply(text="Введите команду как ответ на сообщение "
                                  "пользователя")
    session_generator = get_async_session()
    session = await session_generator.__anext__()
    db_user = await crud_user.get_or_create_user_by_tg_message(
        message.reply_to_message,
        session
    )
    db_user = await crud_user.remove_admin(db_user, session)
    text = f'Администратор {db_user.first_name} {db_user.last_name} удален'
    await message.reply(text=text)
