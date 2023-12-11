import asyncio

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import dbsettings
from models import Base


class Database:

    def __init__(self, ):
        self.engine = create_async_engine(
            dbsettings.database_url_asyncpg
        )
        self.session_factory = async_sessionmaker(self.engine)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def insert_data(self, data: list):
        async with self.session_factory() as session:
            for item in data:
                item_data = {key: getattr(item, key) for key in item.__dict__ if not key.startswith('_')}
                stmt = insert(item.__table__)\
                    .values(item_data)\
                    .on_conflict_do_nothing(index_elements=['order_id'])
                await session.execute(stmt)
            await session.commit()


async def check():
    db = Database()
    await db.create_tables()
    await db.insert_data()


if __name__ == '__main__':
    asyncio.run(check())
