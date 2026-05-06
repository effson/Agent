from pydantic import BaseModel


class QuerySchema(BaseModel):
    query: str

class FeedbackSchema(BaseModel):
    run_id: str
    score: int
