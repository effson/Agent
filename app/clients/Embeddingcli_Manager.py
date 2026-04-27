from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from app.conf.app_config import EmbeddingConfig, app_conf
import asyncio

class EmbeddingClientManager:
    def __init__(self, config: EmbeddingConfig):
        self.client : HuggingFaceEndpointEmbeddings | None = None
        self.config = config

    def _get_client_url(self):
        return f"http://{self.config.host}:{self.config.port}"

    def init(self):
        self.client = HuggingFaceEndpointEmbeddings(model=self._get_client_url()) # BGE: BAAI General Embedding 模型

Embedding_Client_Manager = EmbeddingClientManager(app_conf.embedding)

if __name__ == "__main__":
    Embedding_Client_Manager.init()
    client = Embedding_Client_Manager.client

    async def test():
        text = "What is deep learning?"
        query_result = await client.aembed_query(text)
        print(query_result[:3])

    asyncio.run(test())