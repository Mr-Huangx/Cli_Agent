from tavily import TavilyClient

tavily_client = TavilyClient(api_key="Your Tavily API Key")

def search_web_tool_info():
    return {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "通过互联网搜索最新的信息、新闻或特定问题的答案。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词或问题",
                    },
                },
                "required": ["query"],
            },
        },
    }

def search_web(query):
    """
    当用户询问当前发生的事件、需要查阅最新的网络信息或你不确定的知识时，使用此工具。
    """
    print(f"seach_web_tool联网搜索: {query}...")
    # search 方法会返回一个包含多个搜索结果的字典
    # context=True 会返回合并后的、适合 LLM 阅读的上下文
    response = tavily_client.search(query=query, search_depth="advanced", max_results=3)
    print(f"搜索到 {len(response['results'])} 条结果")
    
    # 将搜索结果拼接成一个字符串返回
    context = [f"标题: {r['title']}\n内容: {r['content']}\n链接: {r['url']}" for r in response['results']]
    return "\n\n".join(context)

