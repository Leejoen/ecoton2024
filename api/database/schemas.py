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
    is_organizer = Column(BOOLEAN(), nullable=False, server_default='0')
    is_department = Column(BOOLEAN(), nullable=False, server_default='0')
    is_active = Column(BOOLEAN(), nullable=False, server_default='0')

    user: Mapped[User] = relationship(
        back_populates='user_addition',
        single_parent=True,
    )


class OrganizerInfo(Base):
    __tablename__ = "organizer_info"

    id = Column(INTEGER(), primary_key=True)
    user_id = Column(ForeignKey(UserInfo.id), nullable=False)
    full_name = Column(VARCHAR(255), nullable=False)
    ogrn = Column(VARCHAR(255), nullable=False)
    ogrn_date = Column(DATE(), nullable=False)
    address = Column(VARCHAR(255), nullable=False)
    format = Column(VARCHAR(255), nullable=False)
    region = Column(VARCHAR(255), nullable=False)
    status = Column(VARCHAR(255), nullable=False)


class MetroLine(Base):
    __tablename__ = "metro_line"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(100), nullable=False)
    color = Column(VARCHAR(50), nullable=False)
    num = Column(VARCHAR(50), nullable=False)
    short = Column(VARCHAR(50), nullable=False)

    line_station: Mapped[MetroStation] = relationship(
        back_populates='line_info',
    )


class MetroStation(Base):
    __tablename__ = "metro_station"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(50), nullable=False)
    line_id = Column(ForeignKey(MetroLine.id), nullable=False)

    line_info: Mapped[MetroLine] = relationship(
        back_populates='line_station',
    )


class EcoEvent(Base):
    __tablename__ = "eco_event"

    id = Column(INTEGER(), primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    short_description = Column(VARCHAR(255), nullable=False)
    description = Column(TEXT(1024), nullable=False)
    date_create = Column(TIMESTAMP(timezone=True), server_default=func.now())
    date_start = Column(TIMESTAMP(), nullable=False)
    place = Column(VARCHAR(255), nullable=False)
    metro_station_id = Column(ForeignKey(MetroStation.id), nullable=True)
    organize_id = Column(ForeignKey(OrganizerInfo.id), nullable=False)

    organize_info: Mapped[OrganizerInfo] = relationship()
    metro_info: Mapped[MetroStation] = relationship()



async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)