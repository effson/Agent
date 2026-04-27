from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker
from app.conf.app_config import DBConfig, app_conf
from sqlalchemy import text
import asyncio

class MySQLClientManager:
    def __init__(self, config: DBConfig):
        self.engine : AsyncEngine | None = None
        self.session_factory = None
        self.config = config

    def _get_client_url(self):
        return f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}?charset=utf8mb4"

    def init(self):
        self.engine = create_async_engine(self._get_client_url(), pool_size=10, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, autoflush=True, expire_on_commit=False)

    async def close(self):
        await self.engine.dispose()

meta_MySQL_Client_Manager = MySQLClientManager(app_conf.db_meta)
dw_MySQL_Client_Manager = MySQLClientManager(app_conf.db_dw)

if __name__ == "__main__":
    dw_MySQL_Client_Manager.init()
    # engine = dw_MySQL_Client_Manager.engine

    async def test():
        async with dw_MySQL_Client_Manager.session_factory() as session:
            sql = "select * from fact_order limit 10"
            result = await session.execute(text(sql))

            rows = result.mappings().fetchall()

            print(rows[0]) # {'order_id': 'ORD20250101001', 'customer_id': 'C001', 'product_id': 'P001', 'date_id': 20250101, 'region_id': 'R001', 'order_quantity': 1, 'order_amount': 8999.0}
            print(rows[0]['order_id']) # ORD20250101001
            print(type(rows))

    asyncio.run(test())