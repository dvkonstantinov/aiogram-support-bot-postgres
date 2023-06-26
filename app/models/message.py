from sqlalchemy import Boolean, ForeignKey, Text, BigInteger
from sqlalchemy.orm import mapped_column, relationship

from app.core.db import Base


class Message(Base):
    """Модель сообщений"""
    telegram_user_id = mapped_column(BigInteger, ForeignKey(
        'user.telegram_id'), nullable=False)
    answer_to_user_id = mapped_column(BigInteger, ForeignKey(
        'user.telegram_id'), nullable=True)
    text = mapped_column(Text, nullable=True)
    attachments = mapped_column(Boolean, default=False)
    telegram_user = relationship('User', backref='messages', foreign_keys=[
        telegram_user_id], lazy='subquery')
    answer_to_user = relationship('User', backref='answers', foreign_keys=[
        answer_to_user_id])

