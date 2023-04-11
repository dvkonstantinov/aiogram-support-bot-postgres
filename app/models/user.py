from sqlalchemy import BigInteger, String, Boolean
from sqlalchemy.orm import mapped_column, relationship

from app.core.db import Base


class User(Base):
    """Модель пользователя телеграм"""

    telegram_id = mapped_column(BigInteger, unique=True, nullable=False)
    telegram_username = mapped_column(String(100), nullable=True)
    is_banned = mapped_column(Boolean, default=False)
    first_name = mapped_column(String(100), nullable=True)
    last_name = mapped_column(String(100), nullable=True)
    is_admin = mapped_column(Boolean, default=False)
    # messages = relationship('Message', backref='telegram_user',
    #                         foreign_keys=[telegram_id])
