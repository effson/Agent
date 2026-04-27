import yaml

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.agent.state import MergedTableInfoState

from app.prompt.prompt_loader import load_prompt
from app.agent.llm import llm

from app.core.log import logger

async def filter_table(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "过滤表格", "status": "running"})

    # 过滤table_infos
    query = state["Query"]
    table_infos = state["Table_infos"]

    try:
        prompt = PromptTemplate(template=load_prompt("filter_table_info"), input_variables=['query','table_infos'])
        output_parser = JsonOutputParser()
        filter_table_chain = prompt | llm | output_parser

        result = await filter_table_chain.ainvoke({"query":query,
                            'table_infos':yaml.dump(table_infos, allow_unicode=True, sort_keys=False)})

        """{
                "fact_order" : ["order_amount", "region_id", ...]
                "dim_region" : ["region_id", "region_name", ...]
            }   
        """
        filterd_table_infos: list[MergedTableInfoState] = []
        for table_info in table_infos:
            if table_info["name"] in result:
                table_info["columns"] = [column for column in table_info["columns"] if column["name"] in result[table_info["name"]]]
                filterd_table_infos.append(table_info)
        c = []
        for table_info in filterd_table_infos:
            for column in table_info["columns"]:
                c.append(column["name"])
        writer({"type": "progress", "step": "过滤表格", "status": "success"})
        logger.info(f"过滤后的表信息：{[filterd_table_info["name"] for filterd_table_info in filterd_table_infos]}")
        logger.info(f"过滤后的字段信息：{c}")
        return {"table_infos": filterd_table_infos}
    except Exception as e:
        writer({"type": "progress", "step": "过滤表格", "status": "error"})
        logger.error(f"过滤表失败:{str(e)}")
        raise