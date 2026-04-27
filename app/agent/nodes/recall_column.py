from langchain_core.output_parsers import JsonOutputParser
from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.entities.column_info import ColumnInfo
from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository

from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def recall_column(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回字段", "status": "running"})

    keywords = state['Keywords']
    query = state["Query"]

    qdrant_column_repository = runtime.context["Qdrant_column_repository"]
    embedding_client = runtime.context["Embedding_client"]

    try:
        # 使用LLM扩展关键词
        # chain = prompt | llm | output_parser
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_column_recall"), input_variables=["query"])

        output_parser = JsonOutputParser()
        extend_chain = prompt | llm | output_parser

        result = await extend_chain.ainvoke({"query": query})

        keywords = list(set(keywords + result))
        logger.info(f"召回字段信息扩展关键词：{keywords}")

        column_infos_map: dict[str, ColumnInfo] = {}
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)
            keyword_column_infos: list[ColumnInfo] = await qdrant_column_repository.search(embedding, score_threshold=0.6, limit=20)
            for column_info in keyword_column_infos:
                if column_info.id not in column_infos_map:
                    column_infos_map[column_info.id] = column_info

        writer({"type": "progress", "step": "召回字段", "status": "success"})
        # retrieved_column_infos: list[ColumnInfo] = list(column_infos_map.values())
        logger.info(f"检索到字段信息: {list(column_infos_map.keys())}")

        return {"Retrieved_column_infos": column_infos_map}
    except Exception as e:
        writer({"type": "progress", "step": "召回字段", "status": "error"})
        logger.error(f"召回字段信息失败: {str(e)}")
        raise