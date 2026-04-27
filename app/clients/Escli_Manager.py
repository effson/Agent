import asyncio
from elasticsearch import AsyncElasticsearch

from app.conf.app_config import EsConfig, app_conf


class ESClientManager:
    def __init__(self, config: EsConfig):
        self.client : AsyncElasticsearch | None = None
        self.config : EsConfig = config

    def _get_client_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = AsyncElasticsearch(
            hosts=[self._get_client_url()],
        )

    async def close(self):
        await self.client.close()

Es_Client_Manager = ESClientManager(app_conf.es)

if __name__ == "__main__":
    Es_Client_Manager.init()
    client = Es_Client_Manager.client

    async def test():
        # Create a new index named books
        # await client.indices.create(
        #     index="books",
        # )

        # add a single document to the books index
        await client.index(
            index="books",
            document={
                "name": "Snow Crash",
                "author": "Neal Stephenson",
                "release_date": "1992-06-01",
                "page_count": 470
            },
        )

        resp = await client.search(
            index="books",
        )

        print(resp)
        await client.close()

    asyncio.run(test())