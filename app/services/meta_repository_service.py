from pathlib import Path
import uuid
from omegaconf import OmegaConf
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from dataclasses import asdict

from app.conf.app_config import app_conf
from app.conf.meta_repository_config import MetaConfig

from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.entities.metric_info import MetricInfo
from app.entities.column_metric import ColumnMetric
from app.entities.example_info import ExampleInfo

from app.repositories.es.value_es_repository import ESValueRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository
from app.repositories.qdrant.example_qdrant_repository import ExampleQdrantRepository

from app.core.log import logger

class MetaRepositoryService:
    def __init__(self, meta_mysql_repository: MetaMySQLRepository,
                        dw_mysql_repository: DWMySQLRepository,
                        qdrant_column_repository: ColumnQdrantRepository,
                        qdrant_metrics_repository: MetricQdrantRepository,
                        qdrant_example_repository: ExampleQdrantRepository,
                        embedding_client: HuggingFaceEndpointEmbeddings,
                        es_value_repository: ESValueRepository):
        self.meta_mysql_repository: MetaMySQLRepository = meta_mysql_repository
        self.dw_mysql_repository: DWMySQLRepository = dw_mysql_repository
        self.qdrant_column_repository = qdrant_column_repository
        self.qdrant_metrics_repository = qdrant_metrics_repository
        self.embedding_client:HuggingFaceEndpointEmbeddings = embedding_client
        self.es_value_repository: ESValueRepository = es_value_repository
        self.qdrant_example_repository: ExampleQdrantRepository = qdrant_example_repository

    async def _save_db_info_to_meta_repository(self, meta_repository_conf: MetaConfig) -> list[ColumnInfo]:
        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []
        for table in meta_repository_conf.tables:
            table_info = TableInfo(
                id=table.name,
                name=table.name,
                role=table.role,
                description=table.description
            )
            table_infos.append(table_info)

            # 查询字段类型
            column_types = await self.dw_mysql_repository.get_column_types(table.name)

            for column in table.columns:
                # 查询字段取值实例
                column_values = await self.dw_mysql_repository.get_column_values(table.name, column.name, 50)

                column_info = ColumnInfo(
                    id=f"{table.name}.{column.name}",
                    name=column.name,
                    type=column_types[column.name],
                    role=column.role,
                    examples=column_values,
                    description=column.description,
                    alias=column.alias,
                    table_id=table.name
                )
                column_infos.append(column_info)

        async with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.save_table_infos(table_infos)
            self.meta_mysql_repository.save_column_infos(column_infos)

        return column_infos

    async def _save_column_info_to_qdrant(self, column_infos: list[ColumnInfo]):
        await self.qdrant_column_repository.ensure_collection()

        points: list[dict] = []
        for column_info in column_infos:

            points.append({
                'id': uuid.uuid4(),
                'embedding_text': column_info.name,
                'payload': asdict(column_info)
            })

            points.append({
                'id': uuid.uuid4(),
                'embedding_text': column_info.description,
                'payload': asdict(column_info)
            })

            for alia in column_info.alias:
                points.append({
                    'id': uuid.uuid4(),
                    'embedding_text': alia,
                    'payload': asdict(column_info)
                })

        # 向量化
        embeddings: list[list[float]] = []

        embedding_texts = [point['embedding_text'] for point in points]
        embedding_batch_size = app_conf.embedding.batch_size
        for i in range(0, len(embedding_texts), embedding_batch_size):
            embedding_texts_batch = embedding_texts[i:i + embedding_batch_size]
            embedding_batch = await self.embedding_client.aembed_documents(embedding_texts_batch)
            embeddings.extend(embedding_batch)

        ids = [point['id'] for point in points]
        payloads = [point['payload'] for point in points]

        await self.qdrant_column_repository.upsert(ids, embeddings, payloads)

    async def _save_example_info_to_qdrant(self, meta_repository_conf: MetaConfig):
        await self.qdrant_example_repository.ensure_collection()

        exclude_types = {
            # 数值类
            "int", "integer", "float", "double", "decimal", "numeric", "bigint",
            # 日期时间类
            "date", "datetime", "timestamp", "time", "year"
        }

        points: list[dict] = []
        for table in meta_repository_conf.tables:
            column_types = await self.dw_mysql_repository.get_column_types(table.name)
            for column in table.columns:
                if (column_types[column.name]).lower() not in exclude_types:
                    column_values = await self.dw_mysql_repository.get_column_values(table.name, column.name, 1000000)
                    for example in column_values:

                        example_info = ExampleInfo(
                                            example=example,
                                            table_column=f"{table.name}.{column.name}",
                                        )
                        points.append({
                            'id': uuid.uuid4(),
                            'embedding_text': example,
                            'payload': asdict(example_info)
                        })

        # 向量化
        embeddings: list[list[float]] = []

        embedding_texts = [point['embedding_text'] for point in points]
        embedding_batch_size = app_conf.embedding.batch_size
        for i in range(0, len(embedding_texts), embedding_batch_size):
            embedding_texts_batch = embedding_texts[i:i + embedding_batch_size]
            embedding_batch = await self.embedding_client.aembed_documents(embedding_texts_batch)
            embeddings.extend(embedding_batch)

        ids = [point['id'] for point in points]
        payloads = [point['payload'] for point in points]

        await self.qdrant_example_repository.upsert(ids, embeddings, payloads)

    async def _save_column_values_to_es(self, meta_repository_conf: MetaConfig):
        await self.es_value_repository.ensure_index()

        es_values: list[ValueInfo] = []
        for table in meta_repository_conf.tables:
            for column in table.columns:
                if column.sync:
                    column_vals = await self.dw_mysql_repository.get_column_values(table.name, column.name, 100000)
                    column_vals_info = [ValueInfo(
                        id=f"{table.name}.{column.name}.{column_val}",
                        value=column_val,
                        column_id=f"{table.name}.{column.name}"
                    ) for column_val in column_vals]
                    es_values.extend(column_vals_info)

        await self.es_value_repository.index(es_values)

    async def _save_metric_to_meta_repository(self, meta_repository_conf: MetaConfig) -> list[MetricInfo]:
        metric_infos: list[MetricInfo] = []
        column_metrics: list[ColumnMetric] = []

        for metric in meta_repository_conf.metrics:
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias
            )
            metric_infos.append(metric_info)

            for column in metric.relevant_columns:
                column_metric = ColumnMetric(
                    column_id=column,
                    metric_id=metric.name
                )
                column_metrics.append(column_metric)

        async with self.meta_mysql_repository.session.begin():
            self.meta_mysql_repository.save_metric_infos(metric_infos)
            self.meta_mysql_repository.save_column_metrics(column_metrics)

        return metric_infos

    async def _save_metric_info_to_qdrant(self, metric_infos: list[MetricInfo]):
        await self.qdrant_metrics_repository.ensure_collection()

        points: list[dict] = []
        for metric_info in metric_infos:
            points.append({
                'id': uuid.uuid4(),
                'embedding_text': metric_info.name,
                'payload': asdict(metric_info)
            })

            points.append({
                'id': uuid.uuid4(),
                'embedding_text': metric_info.description,
                'payload': asdict(metric_info)
            })

            for alia in metric_info.alias:
                points.append({
                    'id': uuid.uuid4(),
                    'embedding_text': alia,
                    'payload': asdict(metric_info)
                })

        # 向量化
        embeddings: list[list[float]] = []

        embedding_texts = [point['embedding_text'] for point in points]
        embedding_batch_size = app_conf.embedding.batch_size
        for i in range(0, len(embedding_texts), embedding_batch_size):
            embedding_texts_batch = embedding_texts[i:i + embedding_batch_size]
            embedding_batch = await self.embedding_client.aembed_documents(embedding_texts_batch)
            embeddings.extend(embedding_batch)

        ids = [point['id'] for point in points]
        payloads = [point['payload'] for point in points]

        await self.qdrant_metrics_repository.upsert(ids, embeddings, payloads)

    async def build(self, conf_path: Path):
        context = OmegaConf.load(conf_path)
        schema = OmegaConf.structured(MetaConfig)

        meta_repository_conf: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        logger.info("加载配置文件成功！")
        # 根据配置文件信息同步指定的表和列的信息
        if meta_repository_conf.tables is not None:
            # 同步表信息, 将表、字段信息保存在meta数据库中
            column_infos = await self._save_db_info_to_meta_repository(meta_repository_conf)
            logger.info("表、字段信息保存到meta数据库成功！")

            # 字段信息建立向量索引->qdrant
            await self._save_column_info_to_qdrant(column_infos)
            logger.info("向量索引保存至qdrant成功！")

            # 字段取值信息建立向量索引->qdrant
            await self._save_example_info_to_qdrant(meta_repository_conf)
            logger.info("字段取值信息保存至qdrant成功！")

            # 对指定的维度字段的取值建立全文索引
            await self._save_column_values_to_es(meta_repository_conf)
            logger.info("指定维度字段的取值建立全文索引成功！")

        if meta_repository_conf.metrics is not None:

            metric_infos = await self._save_metric_to_meta_repository(meta_repository_conf)
            logger.info("metric_info保存到meta数据库成功！")

            await self._save_metric_info_to_qdrant(metric_infos)
            logger.info("metric_info保存到qdrant成功！")