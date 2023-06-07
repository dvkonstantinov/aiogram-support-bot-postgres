import re
from datetime import datetime

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandObject
from aiogram.types import Message, Chat
from dateutil.relativedelta import relativedelta
from app.schemas.user import UserFromDBScheme
from app.schemas.user import UserBaseScheme

DATE_PATTERN = r'^(0?[1-9]|[12][0-9]|3[01]).(0?[1-9]|1[012]).((19|20)\d\d)$'


def extract_user_id(message: Message) -> int:
    text = message.text if message.text else message.caption
    if '#id' not in text:
        return False
    telegram_user_id = int(text.split(sep='#id')[-1])
    return telegram_user_id


def parse_ban_command(command: CommandObject) -> int:
    telegram_user_id = command.args.strip()
    try:
        telegram_user_id = int(telegram_user_id)
    except ValueError:
        return False
    return telegram_user_id


def get_user_name(chat: Chat):
    """Получение полного имени пользователя из чата"""
    if not chat.first_name:
        return ""
    if not chat.last_name:
        return chat.first_name
    return f"{chat.first_name} {chat.last_name}"


def check_input_date_correct(date_args):
    """Проверка интервала дат на соотвествие паттерну"""
    date_from, date_to = date_args.split()
    pattern = re.compile(DATE_PATTERN)
    if not (pattern.match(date_from) and pattern.match(date_to)):
        return False
    return True


def stringdate_to_date(date_args):
    """Конвертация текстового интервала дат в формат datetime"""
    from_date, to_date = date_args.split()
    from_date = datetime.strptime(from_date, '%d.%m.%Y')
    to_date = datetime.strptime(to_date, '%d.%m.%Y') + relativedelta(days=+1)
    return from_date, to_date


def get_user_data(message: Message):
    user_data = {
        'telegram_id': message.from_user.id,
        'telegram_username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
    }
    return user_data


def check_user_is_banned(user: UserBaseScheme):
    return user.is_banned


def check_user_is_admin(user: UserFromDBScheme):
    return user.is_admin


async def get_telegram_user_from_resend_message(message: Message, bot: Bot):
    telegram_user_id = extract_user_id(message.reply_to_message)
    if not telegram_user_id:
        return await message.reply(
            text='Невозможно найти пользователя с таким Id'
        )
    try:
        return await bot.get_chat(telegram_user_id)
    except TelegramAPIError as err:
        return await message.reply(
            text=(f'Невозможно найти пользователя с таким Id. Текст ошибки:\n'
                  f'{err.message}')
        )
