import yaml

from langgraph.runtime import Runtime
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sqlalchemy.ext.asyncio import result

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.agent.llm import llm

from app.prompt.prompt_loader import load_prompt
from app.core.log import logger

async def generate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "生成SQL", "status": "running"})

    query = state["Query"]
    table_infos = state["Table_infos"]
    metric_infos = state["Metric_infos"]
    date_info = state["Date_info"]
    db_info = state["Db_info"]

    try:
        prompt = PromptTemplate(template=load_prompt("generate_sql"),
                                input_variables=["table_infos","metric_infos","date_info","db_info","query"])

        output_parser = StrOutputParser()
        generate_sql_chain = prompt | llm | output_parser

        result = await generate_sql_chain.ainvoke({
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
            "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False),
            "query": query})

        logger.info(f"生成的SQL:{result}")

        return {"Sql":result}
    except Exception as e:
        writer({"type": "progress", "step": "生成SQL", "status": "error"})
        logger.error(f"生成SQL失败: {str(e)}")
        raise