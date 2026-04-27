from typing import TypedDict

from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

from app.repositories.es.value_es_repository import ESValueRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.example_qdrant_repository import ExampleQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository


class DataAgentContext(TypedDict):
    Qdrant_column_repository: ColumnQdrantRepository
    Embedding_client: HuggingFaceEndpointEmbeddings
    Qdrant_metric_repository: MetricQdrantRepository
    Es_value_repository: ESValueRepository
    Qdrant_example_repository: ExampleQdrantRepository
    Meta_mysql_repository: MetaMySQLRepository
    Dw_mysql_repository: DWMySQLRepository