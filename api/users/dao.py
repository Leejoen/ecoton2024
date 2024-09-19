from dao.base import BaseDAO
from database.schemas import User, UserInfo, OrganizerInfo
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert


class UsersDAO(BaseDAO):
    schema = User
    
    @classmethod
    async def create_user(cls, session: AsyncSession, data: dict):
        user = {
            "login": data["login"],
            "password": data.pop('password'),
            "verify_token": data.pop("verify_token"),
        }
        await cls.insert_data(session, user)
        query = await session.execute(
            insert(UserInfo).
            values(**data)
        )
        await session.commit()
        user_id = query.lastrowid
        return user_id
    
    @classmethod
    async def check_user(
        cls,
        session: AsyncSession,
        filters: dict,
    ):
        query = await session.execute(
            select(User.login).
            where(User.verify_token == filters.get("verify_token"))
        )
        result = query.scalar_one_or_none()
        return result


class UsersDAOInfo(BaseDAO):
    schema = UserInfo


class OrganizeInfoDAO(BaseDAO):
    schema = OrganizerInfo