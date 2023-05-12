import re
from datetime import datetime

from aiogram.types import Message, Chat
from dateutil.relativedelta import relativedelta

DATE_PATTERN = r'^(0?[1-9]|[12][0-9]|3[01]).(0?[1-9]|1[012]).((19|20)\d\d)$'


def extract_user_id(message: Message) -> int:
    if message.text:
        text = message.text
    else:
        text = message.caption
    user_id = int(text.split(sep='#id')[-1])
    return user_id


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
