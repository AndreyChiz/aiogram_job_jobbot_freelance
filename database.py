import asyncio
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import Settings
from models import Base, BaseOrderData, UsersOrm


class Database:

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self, ):
        self.engine = create_async_engine(
            Settings().database_url_asyncpg
        )
        self.session_factory = async_sessionmaker(self.engine)

    async def create_tables(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


    # async def insert_data(self, data: list):
    #     async with self.session_factory() as session:
    #         for item in data:
    #             item_data = {key: getattr(item, key) for key in item.__dict__ if not key.startswith('_')}
    #             stmt = insert(item.__table__)\
    #                 .values(item_data)\
    #                 .on_conflict_do_nothing(index_elements=['order_id'])
    #             await session.execute(stmt)
    #         await session.commit()

    async def insert_data(self, data: list):
        inserted_rows = []
        async with self.session_factory() as session:
            for item in data:
                item_data = {key: getattr(item, key) for key in item.__dict__ if not key.startswith('_')}
                stmt = insert(item.__table__) \
                    .values(item_data) \
                    .on_conflict_do_nothing(index_elements=['order_id'])
                result = await session.execute(stmt)
                if result.rowcount > 0:
                    inserted_rows.append(item)
            await session.commit()

        return inserted_rows

    # TODO: ОБЪЕДИНИТЬ

    async def insert_is_notified(self, user_id, user_notify=1):
        user = UsersOrm(user_id=user_id, user_notify=user_notify)
        print(user.user_id, user.user_name, user.user_keywords, user.user_notify)
        async with self.session_factory() as session:
            await session.merge(user)
            await session.commit()


    async  def insert_key_words(self, user_id, user_name, user_keywords):
        user_keywords = user_keywords.split(',') if user_keywords else []
        user = UsersOrm(user_id=user_id, user_name=user_name, user_keywords=user_keywords)
        print(user.user_id, user.user_name, user.user_keywords, user.user_notify)
        async with self.session_factory() as session:
            await session.merge(user)
            await session.commit()

async def check():
    db = Database()
    await db.create_tables()



if __name__ == '__main__':
    asyncio.run(check())
