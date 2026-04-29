## Agent
### 1.项目介绍
Data Agent 是一个基于自然语言处理与数据分析技术的智能数据服务系统，，面向数据仓库应用场景：
- 帮助用户通过对话方式高效获取数据库中的数据，无需掌握复杂的查询语法，可用自然语言提出问题
- 系统自动完成对数据仓库数据的理解、计算分析与结果可视化，大幅提升数据使用效率，降低数据分析门槛，助力业务决策智能化。

### 2.项目架构
- 数据仓库元数据是核心，MySQL存储结构化元数据信息
- Qdrant构建语义向量索引，Elasticsearch 构建全文索引，构建元数据知识库

### 3. Langgraph工作流

<img width="500" height="600" alt="Mermaid" src="https://github.com/user-attachments/assets/df4438a6-4cda-4202-b032-5332dd9101f9" />

### 4.项目运行

<img width="686" height="500" alt="image" src="https://github.com/user-attachments/assets/940be7bd-74e2-4f89-a2fe-6066c8045095" />

<img width="686" height="531" alt="image" src="https://github.com/user-attachments/assets/ebf6512a-ef54-4852-a4c3-8a5ebebafcfb" />


<img width="686" height="531" alt="image" src="https://github.com/user-attachments/assets/054a7688-1eaf-479e-8f39-6a26abcef78f" />


<img width="600" height="531" alt="image" src="https://github.com/user-attachments/assets/62becf2e-a6ed-4467-be1c-7b0eefd186d8" />

<img width="686" height="511" alt="image" src="https://github.com/user-attachments/assets/cc2888d7-6cb4-4752-8cd3-671ec38ab8ac" />

### 5. LangSmith

#### 在.env中添加：
```
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=<your_langsmith_key>
LANGSMITH_PROJECT="Data Agent"
```

<img width="1095" height="325" alt="image" src="https://github.com/user-attachments/assets/2b3f9f25-032e-4fb2-9cfc-5c9c8747fec9" />

<img width="1269" height="562" alt="image" src="https://github.com/user-attachments/assets/31fc4814-a964-47bf-8b6d-198810b90aed" />
