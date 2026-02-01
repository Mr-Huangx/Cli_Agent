# CLI Agent 智能助手

一个基于大语言模型的命令行智能助手系统，具备工具调用、联网搜索、本地知识库检索等能力。

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Agent                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────────────────────────┐  │
│  │   main.py    │─────▶│     Agent/AgentCli.py           │  │
│  │  (入口文件)   │      │  (Agent 核心逻辑)               │  │
│  └──────────────┘      │  - run_agent() 单次对话         │  │
│                        │  - chat_loop() 持续对话         │  │
│                        └──────────────────────────────────┘  │
│                                   │                           │
│                                   ▼                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    ReAct 循环                          │  │
│  │  ┌──────────────┐      ┌──────────────────────────┐   │  │
│  │  │  LLM 推理     │─────▶│  工具调用决策            │   │  │
│  │  │  (DeepSeek)  │      │  (是否需要工具)          │   │  │
│  │  └──────────────┘      └──────────────────────────┘   │  │
│  │         │                        │                      │  │
│  │         │ No                     │ Yes                   │  │
│  │         ▼                        ▼                      │  │
│  │  ┌──────────────┐      ┌──────────────────────────┐   │  │
│  │  │  直接回复     │      │  ToolManager 工具管理器   │   │  │
│  │  └──────────────┘      │  - 工具注册                │   │  │
│  │                        │  - 工具调度                │   │  │
│  └────────────────────────└──────────────────────────┘   │  │
│                                   │                           │
│                                   ▼                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                      Tools 工具层                       │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │ time_tool   │  │weather_tool │  │calculate    │   │  │
│  │  │ (时间查询)   │  │ (天气查询)   │  │ (计算器)     │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  │  ┌─────────────┐  ┌─────────────┐                      │  │
│  │  │search_web   │  │search_local │                      │  │
│  │  │ (联网搜索)   │  │ (本地知识库) │                      │  │
│  │  └─────────────┘  └─────────────┘                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                   │                           │
│                                   ▼                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Memory 记忆层                        │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  ShortTermMemory.py (短期对话历史)               │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
│                                   │                           │
│                                   ▼                           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                   数据存储层                            │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  Chroma 向量数据库 (本地知识库)                 │  │  │
│  │  │  - Aliyun Embedding V4                         │  │  │
│  │  │  - 持久化存储: ./db/chroma_db                  │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

```
cli_agent/
├── Agent/
│   └── AgentCli.py              # Agent 核心逻辑，实现 ReAct 循环
├── Memory/
│   └── ShortTermMemory.py       # 短期记忆管理
├── Tools/
│   ├── ToolManager.py           # 工具管理器（装饰器注册模式）
│   ├── calculate_tool.py        # 计算器工具
│   ├── time_tool.py             # 时间查询工具
│   ├── weather_tool.py          # 天气查询工具
│   ├── search_web_tool.py       # 联网搜索工具（Tavily）
│   ├── search_local_tool.py     # 本地知识库检索工具
│   └── utils/
│       └── rag_utils.py         # RAG 工具（向量数据库、Embedding）
├── db/
│   └── chroma_db/               # Chroma 向量数据库存储
├── main.py                      # 程序入口
├── my_info.txt                  # 本地知识库示例文档
└── README.md                    # 项目说明文档
```

## 核心设计

### 1. Agent 设计 (ReAct 模式)

Agent 采用 **ReAct (Reasoning + Acting)** 模式，通过循环推理和行动来解决问题：

```python
while True:
    # 1. LLM 推理：根据用户输入和工具信息，决定是否需要调用工具
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools_schema
    )
    
    # 2. 判断是否需要工具调用
    if assistant_msg.tool_calls:
        # 3. 执行工具
        func_result = func_to_call(**tool_args)
        # 4. 将工具结果返回给 LLM 继续推理
        messages.append({"role": "tool", "content": str(func_result)})
    else:
        # 5. 直接返回最终答案
        return assistant_msg.content
```

**设计特点**：
- 支持单次对话 (`run_agent`) 和持续对话 (`chat_loop`)
- 自动维护对话历史（短期记忆）
- 工具调用结果自动反馈给 LLM 进行二次推理

### 2. ToolManager 工具管理器

采用 **装饰器模式** 实现工具的自动注册：

```python
class ToolManager:
    def __init__(self):
        self.tools_schema = []      # 工具配置信息（给 LLM 看）
        self.available_tools = {}    # 可执行的工具函数
    
    def register_tool(self, schema):
        """装饰器：自动注册工具"""
        def decorator(func):
            self.available_tools[func.__name__] = func
            self.tools_schema.append(schema)
            return func
        return decorator
```

**使用示例**：

```python
@tool_manager.register_tool(weather_tool_info())
def get_weather(city: str):
    """获取指定城市的天气"""
    weather_data = {"北京": "晴天", "上海": "多云"}
    return weather_data.get(city, f"未知城市{city}的天气")
```

**优势**：
- 新增工具无需修改核心代码，只需添加新文件
- 工具注册自动化，降低维护成本
- 工具配置与实现分离

### 3. 工具层设计

#### 3.1 基础工具

| 工具 | 功能 | 实现方式 |
|------|------|----------|
| `get_weather` | 天气查询 | 模拟数据（可替换为真实 API） |
| `get_current_time` | 时间查询 | Python `datetime` 模块 |
| `calculate` | 数学计算 | 基础四则运算 |

#### 3.2 联网搜索工具

使用 **Tavily API** 实现实时联网搜索：

```python
tavily_client = TavilyClient(api_key="tvly-dev-xxx")

def search_web(query):
    response = tavily_client.search(
        query=query, 
        search_depth="advanced", 
        max_results=3
    )
    return "\n\n".join([f"标题: {r['title']}\n内容: {r['content']}" 
                       for r in response['results']])
```

**应用场景**：
- 查询实时新闻
- 获取最新数据
- 搜索特定问题答案

#### 3.3 本地知识库检索 (RAG)

采用 **RAG (Retrieval-Augmented Generation)** 模式：

```
文档加载 → 文本切片 → 向量化 → 存储到 Chroma → 相似度检索 → 返回结果
```

**技术栈**：
- **Embedding**: 阿里云 DashScope text-embedding-v4
- **向量数据库**: Chroma (持久化存储)
- **文本分割器**: RecursiveCharacterTextSplitter

**实现细节**：

```python
def build_knowledge_base(file_path):
    # 1. 加载文档
    loader = TextLoader(file_path, encoding='utf-8')
    documents = loader.load()
    
    # 2. 切片 (chunk_size=500, overlap=50)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )
    texts = text_splitter.split_documents(documents)
    
    # 3. 向量化并存储
    vector_db = Chroma.from_texts(
        texts=content_list,
        embedding=embeddings,
        persist_directory="./db/chroma_db"
    )

def query_knowledge_base(keyword):
    # 检索并过滤低相关结果（阈值 0.2）
    docs = vector_db.similarity_search_with_relevance_scores(
        keyword, k=10
    )
    valid_results = [doc.page_content for doc, score in docs 
                    if score >= 0.2]
    return "\n---\n".join(valid_results)
```

### 4. 记忆管理

#### 短期记忆

存储最近的对话历史，用于上下文保持：

```python
short_term_memory = [
    {"role": "system", "content": sysytem_prompt},
    {"role": "user", "content": user_input},
    {"role": "assistant", "content": assistant_msg.content},
    {"role": "tool", "content": func_result, "tool_call_id": tool_call.id}
]
```

**特点**：
- 自动维护对话轮次
- 包含工具调用记录
- 支持多轮对话上下文

### 5. System Prompt 设计

采用 **CoT (Chain of Thought)** 思维链引导 LLM：

```python
sysytem_prompt = """
你是一个具备多项工具能力的智能助手。请遵守以下思维链路：
1. 先查后说。根据问题判断是否需要工具调用。
2. 知识库优先准则。
3. 处理工具结果。结合信息给出准确回答。
4. 回答风格。简洁、直接。注明"根据已有记录显示..."。
5. 严禁"马后炮"。需要工具时直接生成调用指令。
"""
```

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| LLM | DeepSeek API (deepseek-chat) |
| 联网搜索 | Tavily API |
| 向量数据库 | Chroma |
| Embedding | 阿里云 DashScope text-embedding-v4 |
| 框架 | LangChain (Community) |
| 语言 | Python 3.x |

## 使用方法

### 1. 安装依赖

```bash
pip install openai tavily-python langchain-community langchain-openai langchain-core chromadb
```

### 2. 配置 API Key

在相应文件中配置以下 API Key：

- **DeepSeek API**: `Agent/AgentCli.py`
- **Tavily API**: `Tools/search_web_tool.py`
- **阿里云 DashScope API**: `Tools/utils/rag_utils.py`

### 3. 构建本地知识库

```python
from Tools.utils.rag_utils import build_knowledge_base
build_knowledge_base("my_info.txt")
```

### 4. 运行程序

```bash
python main.py
```

**运行模式**：
- `test_single_tool()`: 单次对话测试
- `test_agent_chat()`: 持续对话模式

## 示例对话

```
用户: 现在几点了？
Agent 思考: 我需要调用工具 -> get_current_time
工具 get_current_time 返回: 2026-02-01 14:30:25
Agent 回复: 根据已有记录显示，现在的时间是 2026-02-01 14:30:25

用户: aaa老师住哪里？
Agent 思考: 我需要调用工具 -> query_knowledge_base
工具 query_knowledge_base 返回: aaa是我最喜欢的 AI 老师，他住在数字海洋的 1024 号房间。
Agent 回复: 根据已有记录显示，aaa老师住在数字海洋的 1024 号房间。

用户: 今日金价是多少？
Agent 思考: 我需要调用工具 -> search_web
工具 search_web 返回: 标题: 今日金价走势... 内容: ...
Agent 回复: 根据已有记录显示，今日金价为...
```

## 扩展开发

### 添加新工具

1. 在 `Tools/` 目录下创建新工具文件
2. 定义工具 Schema 和实现函数
3. 使用 `@tool_manager.register_tool()` 装饰器注册

**示例**：

```python
from Tools.ToolManager import tool_manager

def my_tool_info():
    return {
        "type": "function",
        "function": {
            "name": "my_tool",
            "description": "工具描述",
            "parameters": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "参数描述"}
                },
                "required": ["param"]
            }
        }
    }

@tool_manager.register_tool(my_tool_info())
def my_tool(param: str):
    """工具实现"""
    return f"处理结果: {param}"
```

## 设计亮点

1. **模块化设计**: Agent、Tools、Memory 层次清晰，职责分离
2. **装饰器模式**: 工具注册自动化，易于扩展
3. **ReAct 循环**: 智能工具调用决策，支持多步推理
4. **RAG 增强**: 本地知识库检索，提升私有数据问答能力
5. **多源知识**: 结合 LLM 内置知识 + 工具外部知识
6. **持久化存储**: 向量数据库持久化，无需重复构建

## 注意事项

- API Key 请妥善保管，不要提交到版本控制
- 本地知识库首次使用前需调用 `build_knowledge_base()` 构建
- 向量数据库存储在 `./db/chroma_db` 目录
- 工具调用失败时会返回错误信息给 LLM 进行二次处理
