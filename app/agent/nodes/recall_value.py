from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.entities.value_info import ValueInfo
from app.entities.column_info import ColumnInfo
from app.entities.example_info import ExampleInfo

from app.core.log import logger

async def recall_value(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段取值", "status": "running"})

    keywords = state['Keywords']
    query = state["Query"]

    qdrant_column_repository = runtime.context["Qdrant_column_repository"]
    qdrant_example_repository = runtime.context["Qdrant_example_repository"]
    embedding_client = runtime.context["Embedding_client"]
    es_value_repository = runtime.context["Es_value_repository"]

    try:
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=["query"])

        output_parser = JsonOutputParser()
        es_value_chain = prompt | llm | output_parser

        result = await es_value_chain.ainvoke({"query": query})

        keywords = list(set(keywords + result))
        logger.info(f"keywords: {keywords}")
        qdrant_example_map: dict[str, ValueInfo] = {}
        es_value_info_map: dict[str, ValueInfo] = {}

        for word in keywords:
            embedding = await embedding_client.aembed_query(word)
            word_example_infos: list[ExampleInfo] = await qdrant_example_repository.search(embedding, score_threshold=0.8, limit=3)
            for example_info in word_example_infos:
                value_id = f"{example_info.table_column}.{example_info.example}"
                if value_id not in qdrant_example_map:
                    qdrant_example_map[value_id] = ValueInfo(
                        id=value_id,
                        value=example_info.example,
                        column_id=example_info.table_column,
                    )
        logger.info(f"qdrant检索到字段取值: {list(qdrant_example_map.keys())}")

        for keyword in keywords:
            ketword_value_info: list[ValueInfo] = await es_value_repository.search(keyword)
            for value_info in ketword_value_info:
                if value_info.id not in es_value_info_map:
                    es_value_info_map[value_info.id] = value_info
        logger.info(f"es检索到字段取值: {list(es_value_info_map.keys())}")

        merged_map = qdrant_example_map | es_value_info_map

        writer({"type": "progress", "step": "召回字段取值", "status": "success"})
        logger.info(f"合并后的字段取值: {list(merged_map.keys())}")
        retrieved_value_infos: list[ValueInfo] = list(merged_map.values())

        return {"Retrieved_value_infos": retrieved_value_infos}
    except Exception as e:
        writer({"type": "progress", "step": "召回字段取值", "status": "error"})
        logger.error(f"召回字段取值失败: {str(e)}")
        raise