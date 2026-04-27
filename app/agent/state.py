from typing import TypedDict, Any

from app.entities.column_info import ColumnInfo
from app.entities.metric_info import MetricInfo
from app.entities.value_info import ValueInfo

class ColumnInfoState(TypedDict):
    name: str
    type: str
    role: str
    examples: list[Any]
    description: str
    alias: list[str]

class MergedTableInfoState(TypedDict):
    name: str
    role: str
    description: str
    columns: list[ColumnInfoState]

class MetricInfoState(TypedDict):
    name: str
    description: str
    relevant_columns: list[str]
    alias: list[str]

class DateInfoState(TypedDict):
    date: str
    weekday: str
    quarter: str

class DbInfoState(TypedDict):
    dialect: str
    version: str

class DataAgentState(TypedDict):
    Query: str # 用户输入的查询
    Keywords: list[str]
    Error: str
    Retrieved_column_infos: dict[str, ColumnInfo]
    Retrieved_metric_infos: list[MetricInfo]
    Retrieved_value_infos: list[ValueInfo]
    Table_infos: list[MergedTableInfoState]
    Metric_infos: list[MetricInfoState]
    Date_info: DateInfoState
    Db_info: DbInfoState
    Sql: str


