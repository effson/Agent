from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct

import numpy as np
import asyncio

from app.conf.app_config import QdrantConfig, app_conf

class AsyncQdrantClientManager:
    def __init__(self, config: QdrantConfig):
        self.client : AsyncQdrantClient | None = None
        self.config : QdrantConfig = config

    def _get_client_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncQdrantClient(url=self._get_client_url())

    async def close(self):
        await self.client.close()

Qdrant_Client_Manager = AsyncQdrantClientManager(app_conf.qdrant)

if __name__ == "__main__":
    Qdrant_Client_Manager.init()
    client = Qdrant_Client_Manager.client


    async def test():
        #Create a collection
        if not await client.collection_exists("test_collection"):
            await client.create_collection(
                collection_name="test_collection",
                vectors_config=VectorParams(size=4, distance=Distance.COSINE), # size定义向量的维度
            )

        # Add vectors
        await client.upsert(
            collection_name="test_collection",
            wait=True,
            points=[  # 行数据格式： id + vector + payload
                PointStruct(id=1, vector=[0.05, 0.61, 0.76, 0.74], payload={"city": "Berlin"}),
                PointStruct(id=2, vector=[0.19, 0.81, 0.75, 0.11], payload={"city": "London"}),
                PointStruct(id=3, vector=[0.36, 0.55, 0.47, 0.94], payload={"city": "Moscow"}),
                PointStruct(id=4, vector=[0.18, 0.01, 0.85, 0.80], payload={"city": "New York"}),
                PointStruct(id=5, vector=[0.24, 0.18, 0.22, 0.44], payload={"city": "Beijing"}),
                PointStruct(id=6, vector=[0.35, 0.08, 0.11, 0.44], payload={"city": "Mumbai"}),
            ],
        )

        # Run a query
        search_result = (await client.query_points(
            collection_name="test_collection",
            query=[0.1, 0.2, 0.3, 0.4],
        )).points

        print(search_result)

        await Qdrant_Client_Manager.close()
    asyncio.run(test())