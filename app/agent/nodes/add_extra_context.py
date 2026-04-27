from langgraph.runtime import Runtime
from datetime import date
from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState, DateInfoState, DbInfoState
from app.repositories.mysql.dw import dw_mysql_repository
from app.core.log import logger

async def add_extra_context(state: DataAgentState, runtime: Runtime[DataAgentContext]):
    writer = runtime.stream_writer
    writer({"type": "progress", "step": "添加额外上下文信息", "status": "running"})

    dw_mysql_repository = runtime.context["Dw_mysql_repository"]
    try:
        day = date.today()
        day_str = day.strftime("%Y-%m-%d")
        weekday = day.strftime("%A")
        quarter = f"Q{(day.month - 1) // 3 + 1}"

        date_info = DateInfoState(date=day_str, weekday=weekday, quarter=quarter)



        db = await dw_mysql_repository.get_db_info()
        db_info = DbInfoState(**db)

        writer({"type": "progress", "step": "添加额外上下文信息", "status": "success"})
        logger.info(f"额外上下文信息：数据库信息-{db_info} 日期信息-{date_info}")
        return {"Date_info": date_info, "Db_info": db_info}

    except Exception as e:
        writer({"type": "progress", "step": "添加额外上下文信息", "status": "error"})
        logger.error(f"添加上下文失败:{str(e)}")
        raise