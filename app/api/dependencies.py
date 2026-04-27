from fastapi import Depends
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.Embeddingcli_Manager import Embedding_Client_Manager
from app.clients.Escli_Manager import Es_Client_Manager
from app.clients.MySQLcli_Manager import meta_MySQL_Client_Manager, dw_MySQL_Client_Manager
from app.clients.Qdrantcli_Manager import Qdrant_Client_Manager
from app.repositories.es.value_es_repository import ESValueRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.qdrant.example_qdrant_repository import ExampleQdrantRepository
from app.services.query_service import QueryService


async def get_meta_session():
    async with meta_MySQL_Client_Manager.session_factory() as session:
        yield session


async def get_dw_session():
    async with dw_MySQL_Client_Manager.session_factory() as session:
        yield session


async def get_embedding_client():
    return Embedding_Client_Manager.client


async def get_column_qdrant_repository():
    return ColumnQdrantRepository(Qdrant_Client_Manager.client)


async def get_value_es_repository():
    return ESValueRepository(Es_Client_Manager.client)


async def get_metric_qdrant_repository():
    return MetricQdrantRepository(Qdrant_Client_Manager.client)

async def get_example_qdrant_repository():
    return ExampleQdrantRepository(Qdrant_Client_Manager.client)

async def get_meta_mysql_repository(session: AsyncSession = Depends(get_meta_session)):
    return MetaMySQLRepository(session)


async def get_dw_mysql_repository(session: AsyncSession = Depends(get_dw_session)):
    return DWMySQLRepository(session)


async def get_query_service(
        embedding_client: HuggingFaceEndpointEmbeddings = Depends(get_embedding_client),
        column_qdrant_repository: ColumnQdrantRepository = Depends(get_column_qdrant_repository),
        example_qdrant_repository: ExampleQdrantRepository = Depends(get_example_qdrant_repository),
        value_es_repository: ESValueRepository = Depends(get_value_es_repository),
        metric_qdrant_repository: MetricQdrantRepository = Depends(get_metric_qdrant_repository),
        meta_mysql_repository: MetaMySQLRepository = Depends(get_meta_mysql_repository),
        dw_mysql_repository: DWMySQLRepository = Depends(get_dw_mysql_repository)
) -> QueryService:
    return QueryService(
        embedding_client=embedding_client,
        column_qdrant_repository=column_qdrant_repository,
        examples_qdrant_repository=example_qdrant_repository,
        value_es_repository=value_es_repository,
        metric_qdrant_repository=metric_qdrant_repository,
        meta_mysql_repository=meta_mysql_repository,
        dw_mysql_repository=dw_mysql_repository
    )