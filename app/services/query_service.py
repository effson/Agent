import json
import uuid
from langchain_huggingface import HuggingFaceEndpointEmbeddings

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.agent.state import DataAgentState
from app.repositories.es.value_es_repository import ESValueRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.qdrant.example_qdrant_repository import ExampleQdrantRepository


class QueryService:
    def __init__(self,
                 embedding_client: HuggingFaceEndpointEmbeddings,
                 column_qdrant_repository: ColumnQdrantRepository,
                 examples_qdrant_repository: ExampleQdrantRepository,
                 value_es_repository: ESValueRepository,
                 metric_qdrant_repository: MetricQdrantRepository,
                 meta_mysql_repository: MetaMySQLRepository,
                 dw_mysql_repository: DWMySQLRepository):
        self.embedding_client = embedding_client
        self.column_qdrant_repository = column_qdrant_repository
        self.examples_qdrant_repository = examples_qdrant_repository
        self.value_es_repository = value_es_repository
        self.metric_qdrant_repository = metric_qdrant_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository

    async def query(self, query: str):
        context = DataAgentContext(
            Embedding_client=self.embedding_client,
            Qdrant_column_repository=self.column_qdrant_repository,
            Qdrant_example_repository=self.examples_qdrant_repository,
            Es_value_repository=self.value_es_repository,
            Qdrant_metric_repository=self.metric_qdrant_repository,
            Meta_mysql_repository=self.meta_mysql_repository,
            Dw_mysql_repository=self.dw_mysql_repository
        )
        state = DataAgentState(Query=query)
        request_run_id = uuid.uuid4()
        config = {
            "run_id": request_run_id,
            "configurable": {
                "thread_id": "some_session_id"  # 线程 ID 建议保留
            }
        }
        try:
            async for chunk in graph.astream(input=state, context=context, stream_mode="custom"):
                if isinstance(chunk, dict) and chunk.get("type") == "result":
                    chunk["run_id"] = request_run_id
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n" # SSE格式发送数据
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False, default=str)}\n\n" 
