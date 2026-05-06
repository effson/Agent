from fastapi import APIRouter
from fastapi.params import Depends
from starlette.responses import StreamingResponse

from app.api.dependencies import get_query_service
from app.api.schemas.query_schema import QuerySchema, FeedbackSchema
from app.services.query_service import QueryService
from langsmith import Client

from dotenv import load_dotenv
load_dotenv()
query_router = APIRouter()

ls_client = Client()

@query_router.post("/api/query")
async def query(
    query: QuerySchema, query_service: QueryService = Depends(get_query_service)
):
    return StreamingResponse(
        query_service.query(query.query), media_type="text/event-stream"
    )
    
@query_router.post("/api/feedback")
async def collect_feedback(feedback: FeedbackSchema):
    try:
        # 将前端的 0/1 评分发送到 LangSmith
        # key: 可以自定义，比如 "user_score" 或 "correctness"
        ls_client.create_feedback(
            run_id=feedback.run_id,
            key="User_Score",
            score=feedback.score,
            comment="！！！用户反馈差评" if feedback.score == 0 else None
        )

        return {"status": "success", "message": "Feedback logged to LangSmith"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
