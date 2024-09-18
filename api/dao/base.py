from sqlalchemy import delete, select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession


class BaseDAO:
    schema = None

    @classmethod
    async def find_id_by_id(cls, session: AsyncSession, obj_id):
        query = select(cls.schema.id).filter_by(id=obj_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @classmethod
    async def find_one_or_none(cls, session: AsyncSession, filters: dict):
        query = select(cls.schema).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @classmethod
    async def insert_data(cls, session: AsyncSession, data: dict):
        query = await session.execute(
            insert(cls.schema).
            values(**data)
        )
        await session.commit()
        return query.lastrowid
    
    @classmethod
    async def update_data(
        cls,
        session: AsyncSession,
        values: dict,
        filters: dict,
    ):
        await session.execute(
            update(cls.schema).
            filter_by(**filters).
            values(**values)
        )
        await session.commit()

    @classmethod
    async def delete_data(
        cls,
        session: AsyncSession,
        filters: dict,
    ):
        await session.execute(
            delete(cls.schema).
            filter_by(**filters)
        )
        await session.commit()