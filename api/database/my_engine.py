from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from database.config import MYSQL

engine = create_async_engine(
    f'mysql+asyncmy://{MYSQL.get("user")}:{MYSQL.get("password")}@localhost/{MYSQL.get("database")}',
    echo=MYSQL.get('echo'),
    pool_recycle=3600
)

asyns_connection = sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with asyns_connection() as session:
        yield session