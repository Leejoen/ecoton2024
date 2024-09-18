from __future__ import annotations
from sqlalchemy import Column, ForeignKey, Table, select, insert, func
from sqlalchemy.dialects.mysql import (
    INTEGER,
    VARCHAR,
    TIMESTAMP,
    BOOLEAN,
    TEXT,
    DATE
)
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped
from database.my_engine import engine


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    login = Column(VARCHAR(50), primary_key=True)
    password = Column(VARCHAR(255), nullable=False)
    is_active = Column(BOOLEAN(), nullable=False, server_default='1')
    date_create = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user_addition: Mapped[UserInfo] = relationship(
        back_populates='user',
    )


class UserInfo(Base):
    __tablename__ = "user_info"

    id = Column(INTEGER(), primary_key=True)
    login = Column(
        ForeignKey(
            User.login,
            onupdate='cascade',
            ondelete='cascade',
        ),
        nullable=False,
    )
    first_name = Column(VARCHAR(100), nullable=False)
    second_name = Column(VARCHAR(100), nullable=False)
    last_name = Column(VARCHAR(100), nullable=True)

    user: Mapped[User] = relationship(
        back_populates='user_addition',
        single_parent=True,
    )