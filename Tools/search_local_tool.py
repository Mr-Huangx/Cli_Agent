from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
import json
from Tools.ToolManager import tool_manager
import os
from openai import OpenAI
from Tools.utils.rag_utils import embeddings


PERSIST_DIRECTORY = "./db/chroma_db"

def search_local_knowledge_info():
    return {
        "type": "function",
        "function": {
            "name": "query_knowledge_base",
            "description": "当用户询问关于公司内部资料、私有文档或特定业务知识时使用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "用于检索的关键词或问题描述"}
                },
                "required": ["keyword"]
            },
        }
    }

@tool_manager.register_tool(search_local_knowledge_info())
def query_knowledge_base(keyword):
    """检索本地知识库"""
    print(f"agent正在私有知识库中检索: {keyword}...")
    
    # 加载已有的数据库
    vector_db = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
    
    # 检索前 10 个最相关的片段，之后再重排
    docs = vector_db.similarity_search_with_relevance_scores(keyword, k=10)

    # 设定一个硬性阈值 0.2
    score_threshold = 0.2
    
    valid_results = []
    for doc, score in docs:
        if score >= score_threshold:
            valid_results.append(doc.page_content)
            print(f"匹配成功！得分: {round(score, 4)}")
        else:
            print(f"舍弃低相关片段，得分: {round(score, 4)}")

    if not valid_results:
        print("❌ 本地知识库未找到高度相关的匹配项。")
        return "本地知识库中未找到关于该问题的确切记录。"
    return "\n---\n".join(valid_results)