from Tools.weather_tool import get_weather_tool_info, get_weather
from Tools.time_tool import get_current_time, time_tool_info
from openai import OpenAI
from Agent.AgentCli import run_agent,chat_loop
from Tools.calculate_tool import calculate_tool_info, calculate
from Tools.search_web_tool import search_web_tool_info, search_web

if __name__ == "__main__":
    tools_schema = []
    tools_schema.append(get_weather_tool_info())
    tools_schema.append(time_tool_info())
    tools_schema.append(calculate_tool_info())
    tools_schema.append(search_web_tool_info())

    available_tools = {
        "get_weather": get_weather,
        "get_current_time": get_current_time,
        "calculate": calculate,
        "search_web": search_web,
    }

    #  测试 1：普通闲聊
    # print("\n--- 测试 1 ---")
    # print("最终回复:", run_agent("你好，你是谁？", tools_schema, available_tools))
    
    # 测试 2：需要调用工具（时间）
    # print("\n--- 测试 2 ---")
    # print("最终回复:", run_agent("现在几点了？", tools_schema, available_tools))

    # 测试 3：需要调用工具（天气）
    # print("\n--- 测试 3 ---")
    # print("最终回复:", run_agent("帮我查一下上海的天气，我想知道要不要带伞。", tools_schema, available_tools))

    # # 测试 4：需要调用工具（计算）
    # print("\n--- 测试 4 ---")
    # print("最终回复:", run_agent("计算 1+1", tools_schema, available_tools))

    # 测试 5：需要调用工具（联网搜索）
    # print("\n--- 测试 5 ---")
    # print("最终回复:", run_agent("今日金价是多少？", tools_schema, available_tools))

    # 启动聊天循环
    # chat_loop(tools_schema, available_tools)
