from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.message import crud_message


async def get_report_from_db(session: AsyncSession,
                             from_date=None,
                             to_date=None):
    """Получение отчета за интервал времени из базы данных.
    :param session: Асинхронная сессия к БД
    :type session: AsyncSession
    :param from_date: Дата начала
    :type from_date: str
    :param to_date: Дата окончания
    :type to_date: str
    :return: Возвращает словарь с данными для отчета
    :rtype: dict
    """
    if not to_date:
        to_date = datetime.now()
    if not from_date:
        from_date = to_date + relativedelta(months=-1)
    messages = await crud_message.get_by_date_interval(
        from_date, to_date, session
    )
    users_senders = []
    answers_amount = 0
    questions_amount = 0

    for mes in messages:
        if (mes.telegram_user_id not in users_senders
                and not mes.answer_to_user_id):
            users_senders.append(mes.telegram_user_id)
        if mes.answer_to_user_id:
            answers_amount += 1
        else:
            questions_amount += 1
    users_amount = len(users_senders)
    report = {
        'from_date': from_date.strftime('%d.%m.%Y'),
        'to_date': to_date.strftime('%d.%m.%Y'),
        'users_amount': users_amount,
        'answers_amount': answers_amount,
        'questions_amount': questions_amount,
    }
    return report
