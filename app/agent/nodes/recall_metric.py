from langgraph.runtime import Runtime
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.agent.llm import llm
from app.prompt.prompt_loader import load_prompt
from app.entities.metric_info import MetricInfo
from langsmith import traceable

from app.core.log import logger
from dotenv import load_dotenv
load_dotenv()

@traceable(run_type="chain", name="recall_metric")
async def recall_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "召回指标", "status": "running"})

    keywords = state['Keywords']
    query = state["Query"]

    embedding_client = runtime.context["Embedding_client"]
    qdrant_metric_repository = runtime.context["Qdrant_metric_repository"]
    try:
        prompt = PromptTemplate(template=load_prompt("extend_keywords_for_metric_recall"), input_variables=["query"])

        output_parser = JsonOutputParser()
        metric_chain = prompt | llm | output_parser

        result = await metric_chain.ainvoke({"query": query})
        keywords = list(set(keywords + result))

        metric_infos_map: dict[str, MetricInfo] = {}
        for keyword in keywords:
            embedding = await embedding_client.aembed_query(keyword)
            keyword_metric_infos: list[MetricInfo] = await qdrant_metric_repository.search(embedding, score_threshold=0.6,
                                                                                           limit=20)
            for metric_info in keyword_metric_infos:
                if metric_info.name not in metric_infos_map:
                    metric_infos_map[metric_info.id] = metric_info

        retrieved_metric_infos: list[MetricInfo] = list(metric_infos_map.values())

        writer({"type": "progress", "step": "召回指标", "status": "success"})
        logger.info(f"检索到指标信息: {list(metric_infos_map.keys())}")

        return {"Retrieved_metric_infos": retrieved_metric_infos}
    except Exception as e:
        writer({"type": "progress", "step": "召回指标", "status": "error"})
        logger.error(f"召回指标信息失败: {str(e)}")
        raise
