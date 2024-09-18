from dao.base import BaseDAO
from database.schemas import User, UserInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


class UsersDAO(BaseDAO):
    schema = User
    
    @classmethod
    async def create_user(cls, session: AsyncSession, data: dict):
        user = {
            "login": data["login"],
            "password": data.pop('password')
        }
        await cls.insert_data(session, user)
        query = await session.execute(
            insert(UserInfo).
            values(**data)
        )
        await session.commit()
        user_id = query.lastrowid
        return user_id


class UsersDAOInfo(BaseDAO):
    schema = UserInfo