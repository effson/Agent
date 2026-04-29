from langgraph.runtime import Runtime
import yaml

from app.agent.llm import llm
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.prompt.prompt_loader import load_prompt
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from app.core.log import logger
from langsmith import traceable
from dotenv import load_dotenv
load_dotenv()

@traceable(run_type="chain", name="filter_metric")
async def filter_metric(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤指标", "status": "running"})

    query = state["Query"]
    metric_infos = state["Metric_infos"]
    try:
        prompt = PromptTemplate(template=load_prompt("filter_metric_info"), input_variables=['query', 'metric_infos'])

        output_parser = JsonOutputParser()
        filter_metric_chain = prompt | llm | output_parser

        result = await filter_metric_chain.ainvoke({"query": query,
                                                    'metric_infos': yaml.dump(metric_infos, allow_unicode=True,
                                                                            sort_keys=False)})

        metric_infos = [metric_info for metric_info in metric_infos if metric_info["name"] in result]
        writer({"type": "progress", "step": "过滤指标", "status": "success"})
        logger.info(f"过滤后的指标信息: {[metric_info["name"] for metric_info in metric_infos]}")
        return {"Metric_infos": metric_infos}
    except Exception as e:
        writer({"type": "progress", "step": "过滤指标", "status": "error"})
        logger.error(f"过滤指标失败:{str(e)}")
        raise
