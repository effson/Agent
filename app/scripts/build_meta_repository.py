import argparse
import asyncio
from pathlib import Path

from app.clients.MySQLcli_Manager import meta_MySQL_Client_Manager, dw_MySQL_Client_Manager
from app.clients.Qdrantcli_Manager import Qdrant_Client_Manager
from app.clients.Embeddingcli_Manager import Embedding_Client_Manager
from app.clients.Escli_Manager import Es_Client_Manager

from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.example_qdrant_repository import ExampleQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.es.value_es_repository import ESValueRepository

from app.services.meta_repository_service import MetaRepositoryService

async def build(conf_path: Path):
    meta_MySQL_Client_Manager.init()
    dw_MySQL_Client_Manager.init()
    Qdrant_Client_Manager.init()
    Embedding_Client_Manager.init()
    Es_Client_Manager.init()

    async with meta_MySQL_Client_Manager.session_factory() as meta_session, dw_MySQL_Client_Manager.session_factory() as dw_session:
        meta_mysql_repository: MetaMySQLRepository = MetaMySQLRepository(meta_session)
        dw_mysql_repository: DWMySQLRepository = DWMySQLRepository(dw_session)

        qdrant_column_repository = ColumnQdrantRepository(Qdrant_Client_Manager.client)
        qdrant_metrics_repository = MetricQdrantRepository(Qdrant_Client_Manager.client)
        qdrant_example_repository = ExampleQdrantRepository(Qdrant_Client_Manager.client)

        es_value_repository = ESValueRepository(Es_Client_Manager.client)

        meta_repository_service = MetaRepositoryService(meta_mysql_repository=meta_mysql_repository,
                                                        dw_mysql_repository=dw_mysql_repository,
                                                        qdrant_column_repository=qdrant_column_repository,
                                                        qdrant_metrics_repository=qdrant_metrics_repository,
                                                        qdrant_example_repository=qdrant_example_repository,
                                                        embedding_client=Embedding_Client_Manager.client,
                                                        es_value_repository=es_value_repository)
        await meta_repository_service.build(conf_path)
    await meta_MySQL_Client_Manager.close()
    await dw_MySQL_Client_Manager.close()
    await Qdrant_Client_Manager.close()
    await Es_Client_Manager.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf")

    args = parser.parse_args()
    config_path = args.conf

    asyncio.run(build(Path(config_path)))
