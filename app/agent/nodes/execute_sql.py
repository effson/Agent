from langgraph.runtime import Runtime

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.core.log import logger

async def execute_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "执行SQL", "status": "running"})

    sql = state["Sql"]

    try:
        dw_mysql_repository = runtime.context["Dw_mysql_repository"]
        result = await dw_mysql_repository.excute_sql(sql)
        writer({"type": "progress", "step": "执行SQL", "status": "success"})
        writer({"type": "result", "data": result})

        logger.info(f"SQL执行结果：{result}")

    except Exception as e:
        writer({"type": "progress", "step": "执行SQL", "status": "error"})
        logger.error(f"执行SQL失败:{str(e)}")
        raise