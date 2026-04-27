import asyncio

from langgraph.graph import StateGraph
from langgraph.constants import START, END

from app.agent.context import DataAgentContext
from app.agent.state import DataAgentState

from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.regulate_sql import regulate_sql
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.merge_retrieved import merge_retrieved
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.validate_sql import validate_sql

from app.clients.Embeddingcli_Manager import Embedding_Client_Manager
from app.clients.Escli_Manager import Es_Client_Manager
from app.clients.MySQLcli_Manager import meta_MySQL_Client_Manager, dw_MySQL_Client_Manager
from app.clients.Qdrantcli_Manager import Qdrant_Client_Manager
from app.repositories.es.value_es_repository import ESValueRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository

from app.repositories.qdrant.column_qdrant_repository import ColumnQdrantRepository
from app.repositories.qdrant.example_qdrant_repository import ExampleQdrantRepository
from app.repositories.qdrant.metric_qdrant_repository import MetricQdrantRepository

graph_builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("recall_column", recall_column)
graph_builder.add_node("recall_value", recall_value)
graph_builder.add_node("recall_metric", recall_metric)
graph_builder.add_node("merge_retrieved", merge_retrieved)
graph_builder.add_node("filter_metric", filter_metric)
graph_builder.add_node("filter_table", filter_table)
graph_builder.add_node("add_extra_context", add_extra_context)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("validate_sql", validate_sql)
graph_builder.add_node("regulate_sql", regulate_sql)
graph_builder.add_node("execute_sql", execute_sql)

graph_builder.add_edge(START, "extract_keywords")
graph_builder.add_edge("extract_keywords", "recall_column")
graph_builder.add_edge("extract_keywords", "recall_value")
graph_builder.add_edge("extract_keywords", "recall_metric")
graph_builder.add_edge("recall_column", "merge_retrieved")
graph_builder.add_edge("recall_value", "merge_retrieved")
graph_builder.add_edge("recall_metric", "merge_retrieved")
graph_builder.add_edge("merge_retrieved", "filter_table")
graph_builder.add_edge("merge_retrieved", "filter_metric")
graph_builder.add_edge("filter_table", "add_extra_context")
graph_builder.add_edge("filter_metric", "add_extra_context")
graph_builder.add_edge("add_extra_context", "generate_sql")
graph_builder.add_edge("generate_sql", "validate_sql")

graph_builder.add_conditional_edges(source="validate_sql",
                                    path=lambda state: "execute_sql" if state["Error"] is None else "regulate_sql",
                                    path_map={"execute_sql": "execute_sql", "regulate_sql": "regulate_sql"}
                                    )

graph_builder.add_edge("regulate_sql", "execute_sql")
graph_builder.add_edge("execute_sql", END)

graph = graph_builder.compile()

# print(graph.get_graph().draw_mermaid())

if __name__ == "__main__":
    async def test():
        Qdrant_Client_Manager.init()
        Embedding_Client_Manager.init()
        Es_Client_Manager.init()
        meta_MySQL_Client_Manager.init()
        dw_MySQL_Client_Manager.init()

        async with meta_MySQL_Client_Manager.session_factory() as meta_session, dw_MySQL_Client_Manager.session_factory() as dw_session:
            meta_mysql_repository = MetaMySQLRepository(meta_session)
            dw_mysql_repository = DWMySQLRepository(dw_session)
            qdrant_column_repository = ColumnQdrantRepository(Qdrant_Client_Manager.client)
            qdrant_metric_repository = MetricQdrantRepository(Qdrant_Client_Manager.client)
            qdrant_example_repository = ExampleQdrantRepository(Qdrant_Client_Manager.client)

            embedding_client = Embedding_Client_Manager.client
            es_value_repository = ESValueRepository(Es_Client_Manager.client)

            state = DataAgentState(Query="查询华北地区的销售额")
            context = DataAgentContext(Qdrant_column_repository=qdrant_column_repository,
                                       Embedding_client=embedding_client,
                                       Qdrant_metric_repository=qdrant_metric_repository,
                                       Es_value_repository=es_value_repository,
                                       Qdrant_example_repository=qdrant_example_repository,
                                       Meta_mysql_repository=meta_mysql_repository,
                                       Dw_mysql_repository=dw_mysql_repository)

            async for chuck in graph.astream(input=state,context=context,stream_mode="custom"):
                print(chuck)

        await Qdrant_Client_Manager.close()
        await Es_Client_Manager.close()
    asyncio.run(test())