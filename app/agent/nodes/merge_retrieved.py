from typing import TypedDict

from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, ColumnInfoState, MergedTableInfoState, MetricInfoState
from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.repositories.mysql.meta import meta_mysql_repository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.core.log import logger


async def merge_retrieved(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "合并召回信息", "status": "running"})

    retrieved_column_infos: dict[str, ColumnInfo] = state["Retrieved_column_infos"]
    retrieved_metric_infos: list[MetricInfo] = state["Retrieved_metric_infos"]
    retrieved_value_infos: list[ValueInfo] = state["Retrieved_value_infos"]

    meta_mysql_repository = runtime.context["Meta_mysql_repository"]

    try:
        # 合并指标所需字段(列)信息和已检索到的字段信息
        for retrieved_metric_info in retrieved_metric_infos:
            for relevant_column in retrieved_metric_info.relevant_columns:
                if relevant_column not in retrieved_column_infos:
                    column_info: ColumnInfo = await meta_mysql_repository.get_column_info_by_id(relevant_column)
                    retrieved_column_infos[relevant_column] = column_info

        # 将检索到的所需字段的取值添加到该字段的examples列表中
        for retrieved_value_info in retrieved_value_infos:
            column_id = retrieved_value_info.column_id
            if column_id not in retrieved_column_infos:
                column_info: ColumnInfo = await meta_mysql_repository.get_column_info_by_id(column_id)
                retrieved_column_infos[column_id] = column_info
            value = retrieved_value_info.value
            if value not in retrieved_column_infos[column_id].examples:
                retrieved_column_infos[column_id].examples.append(value)

        #合并列信息，属于同一个表的列放到一个列表中
        table_column_map: dict[str, list[ColumnInfo]] = {}
        for retrieved_column_info in retrieved_column_infos.values():
            table_id = retrieved_column_info.table_id
            if table_id not in table_column_map:
                table_column_map[table_id] = []
            table_column_map[table_id].append(retrieved_column_info)

        # 为每个表添加主外键字段信息
        for table_id in table_column_map.keys():
            key_columns: list[ColumnInfo] = await meta_mysql_repository.get_key_columns_by_id(table_id)
            column_ids = [column_info.id for column_info in table_column_map[table_id]]
            for key_column in key_columns:
                if key_column.id not in column_ids:
                    table_column_map[table_id].append(key_column)

        # 生成 表信息和以及其中的列信息
        table_infos: list[MergedTableInfoState] = []
        for table_id, column_infos in table_column_map.items():
            table_info: TableInfo = await meta_mysql_repository.get_table_info_by_id(table_id)
            table_columns = [ColumnInfoState(
                name=column_info.name,
                type=column_info.type,
                role=column_info.role,
                examples=column_info.examples,
                description=column_info.description,
                alias=column_info.alias
            ) for column_info in column_infos]
            merged_table_state = MergedTableInfoState(
                name=table_info.name,
                role=table_info.role,
                description=table_info.description,
                columns=table_columns
            )

            table_infos.append(merged_table_state)

        # 处理指标信息
        metric_infos: list[MetricInfoState] = [MetricInfoState(
            name=retrieved_metric_info.name,
            description=retrieved_metric_info.description,
            relevant_columns=retrieved_metric_info.relevant_columns,
            alias=retrieved_metric_info.alias
        ) for retrieved_metric_info in retrieved_metric_infos]

        writer({"type": "progress", "step": "合并召回信息", "status": "success"})
        logger.info(
            f"合并召回信息: 表信息-{[table_info['name'] for table_info in table_infos]},指标信息-{[metric_info['name'] for metric_info in metric_infos]}")
        return {
            "Table_infos": table_infos,
            "Metric_infos": metric_infos
        }
    except Exception as e:
        writer({"type": "progress", "step": "合并召回信息", "status": "error"})
        logger.error(f"合并召回信息失败: {str(e)}")
        raise