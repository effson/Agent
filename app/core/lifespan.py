from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.clients.Embeddingcli_Manager import Embedding_Client_Manager
from app.clients.Escli_Manager import Es_Client_Manager
from app.clients.MySQLcli_Manager import meta_MySQL_Client_Manager, dw_MySQL_Client_Manager
from app.clients.Qdrantcli_Manager import Qdrant_Client_Manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 应用启动前执行
    Embedding_Client_Manager.init()
    Qdrant_Client_Manager.init()
    Es_Client_Manager.init()
    meta_MySQL_Client_Manager.init()
    dw_MySQL_Client_Manager.init()
    yield
    # FastAPI 应用结束前执行

    await Qdrant_Client_Manager.close()
    await Es_Client_Manager.close()
    await meta_MySQL_Client_Manager.close()
    await dw_MySQL_Client_Manager.close()
