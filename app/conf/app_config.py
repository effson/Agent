from pathlib import Path
from dataclasses import dataclass
from omegaconf import OmegaConf
from typing import Optional

@dataclass
class LogConfig:
    enable: bool
    level: str
    path: Optional[str] = None      # 只有文件日志需要 path
    rotation: Optional[str] = None  # 只有文件日志需要 rotation
    retention: Optional[str] = None # 只有文件日志需要 retention

@dataclass
class ConsoleConfig:
    enable: bool
    level: str

@dataclass
class Logging:
    file: LogConfig
    console: ConsoleConfig

@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int

@dataclass
class EmbeddingConfig:
    host: str
    port: int
    batch_size: int
    model: str

@dataclass
class EsConfig:
    host: str
    port: int
    index_name: str

@dataclass
class LlmConfig:
    model_name: str
    api_key: str
    base_url: str

@dataclass
class AppConfig:
    logging: Logging
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: EsConfig
    llm: LlmConfig

config_file = Path(__file__).parents[2] / 'conf' / 'app_config.yaml'
content = OmegaConf.load(config_file)

schema = OmegaConf.structured(AppConfig)

app_conf: AppConfig = OmegaConf.to_object(OmegaConf.merge(schema, content))

# print(app_conf.logging.file.level)
# print(app_conf.embedding.model)
# print(app_conf.db_dw.password)
# print(app_conf.db_meta.password)