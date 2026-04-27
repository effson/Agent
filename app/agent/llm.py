from langchain_anthropic import ChatAnthropic

from app.conf.app_config import app_conf

llm = ChatAnthropic(
    model=app_conf.llm.model_name,
    anthropic_api_key=app_conf.llm.api_key,
    anthropic_api_url=app_conf.llm.base_url,
    temperature=0
)