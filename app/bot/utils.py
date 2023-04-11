from aiogram.types import Message, Chat


def extract_user_id(message: Message) -> int:
    if message.text:
        text = message.text
    else:
        text = message.caption
    user_id = int(text.split(sep='#id')[-1])
    return user_id


def get_user_name(chat: Chat):
    if not chat.first_name:
        return ""
    if not chat.last_name:
        return chat.first_name
    return f"{chat.first_name} {chat.last_name}"
