from langgraph.runtime import Runtime
from langsmith import traceable

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.core.log import logger
from dotenv import load_dotenv
load_dotenv()

@traceable
async def validate_sql(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "验证SQL", "status": "running"})

    sql = state["Sql"]

    dw_mysql_repository: DWMySQLRepository = runtime.context["Dw_mysql_repository"]
    try:
        await dw_mysql_repository.validate_sql(sql)

        writer({"type": "progress", "step": "验证SQL", "status": "success"})
        logger.info(f"SQL语法正确")
        return {'Error': None}
    except Exception as e:
        writer({"type": "progress", "step": "验证SQL", "status": "error"})
        logger.info(f"SQL语法错误：{str(e)}")
        return {'Error': str(e)}
