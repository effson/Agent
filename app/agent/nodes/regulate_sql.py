from langgraph.runtime import Runtime
import yaml
from langsmith import traceable

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.prompt.prompt_loader import load_prompt
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.agent.llm import llm
from app.core.log import logger
from dotenv import load_dotenv
load_dotenv()


@traceable(run_type="chain", name="regulate_sql")
async def regulate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "校正SQL", "status": "running"})

    query = state["Query"]
    table_infos = state["Table_infos"]
    metric_infos = state["Metric_infos"]
    date_info = state["Date_info"]
    db_info = state["Db_info"]
    error = state["Error"]
    sql = state["Sql"]

    try:
        prompt = PromptTemplate(template=load_prompt("regulate_sql"),
                                input_variables=["table_infos", "metric_infos", "date_info", "db_info", "query", "sql", "error" ])

        output_parser = StrOutputParser()
        regulate_sql_chain = prompt | llm | output_parser

        result = await regulate_sql_chain.ainvoke({
            "table_infos": yaml.dump(table_infos, allow_unicode=True, sort_keys=False),
            "metric_infos": yaml.dump(metric_infos, allow_unicode=True, sort_keys=False),
            "date_info": yaml.dump(date_info, allow_unicode=True, sort_keys=False),
            "db_info": yaml.dump(db_info, allow_unicode=True, sort_keys=False),
            "query": query, "sql": sql, "error": error})

        logger.info(f"校正后的SQL:{result}")

        return {"Sql": result}
    except Exception as e:
        writer({"type": "progress", "step": "校正SQL", "status": "error"})
        logger.error(f"校正SQL失败:{str(e)}")
        raise
