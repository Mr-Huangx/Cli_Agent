from Tools.ToolManager import tool_manager
from openai import OpenAI
from Agent.AgentCli import run_agent,chat_loop
import Tools.weather_tool
import Tools.time_tool
import Tools.calculate_tool
import Tools.search_web_tool

def test_single_tool():
    #  测试 1：普通闲聊
    print("\n--- 测试 1 ---")
    print("最终回复:", run_agent("你好，你是谁？", tools_schema, available_tools))
    
    # 测试 2：需要调用工具（时间）
    print("\n--- 测试 2 ---")
    print("最终回复:", run_agent("现在几点了？", tools_schema, available_tools))

    # 测试 3：需要调用工具（天气）
    print("\n--- 测试 3 ---")
    print("最终回复:", run_agent("帮我查一下上海的天气，我想知道要不要带伞。", tools_schema, available_tools))

    # 测试 4：需要调用工具（计算）
    print("\n--- 测试 4 ---")
    print("最终回复:", run_agent("计算 1+1", tools_schema, available_tools))

    # 测试 5：需要调用工具（联网搜索）    
    # print("\n--- 测试 5 ---")
    # print("最终回复:", run_agent("今日金价是多少？", tools_schema, available_tools))

def test_agent_chat():
    # 启动聊天循环
    chat_loop(tools_schema, available_tools)


if __name__ == "__main__":

    # 直接获取注册好的结果
    tools_schema = tool_manager.tools_schema
    available_tools = tool_manager.available_tools
    print(f"已自动加载工具: {list(available_tools.keys())}")
    print(f"已自动加载工具配置: {tools_schema}")

    # 测试单一的工具调用
    test_single_tool()
    
    # agent正常对话测试
    # test_agent_chat()
