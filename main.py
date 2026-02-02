from Tools.ToolManager import tool_manager
from openai import OpenAI
from Agent.AgentCli import run_agent,chat_loop
import Tools.weather_tool
import Tools.time_tool
import Tools.calculate_tool
import Tools.search_web_tool
import Tools.search_local_tool
from Tools.utils.rag_utils import build_knowledge_base
from Agent.LangGraphAgent import MyLangGraphAgent
import os


def test_single_tool():
    #  测试 1：普通闲聊
    # print("\n--- 测试 1 ---")
    # print("最终回复:", run_agent("你好，你是谁？", tools_schema, available_tools))
    
    # # 测试 2：需要调用工具（时间）
    # print("\n--- 测试 2 ---")
    # print("最终回复:", run_agent("现在几点了？", tools_schema, available_tools))

    # # 测试 3：需要调用工具（天气）
    # print("\n--- 测试 3 ---")
    # print("最终回复:", run_agent("帮我查一下上海的天气，我想知道要不要带伞。", tools_schema, available_tools))

    # # 测试 4：需要调用工具（计算）
    # print("\n--- 测试 4 ---")
    # print("最终回复:", run_agent("计算 1+1", tools_schema, available_tools))

    # # 测试 5：需要调用工具（联网搜索）    
    # print("\n--- 测试 5 ---")
    # print("最终回复:", run_agent("今日金价是多少？", tools_schema, available_tools))

    # # 测试 6：需要调用工具（本地知识库搜索）
    # print("\n--- 测试 6 ---")
    # print("最终回复:", run_agent("公司最近有什么新的项目？", tools_schema, available_tools))

    # 先构建知识库
    # build_knowledge_base("my_info.txt")

    # 测试 7：需要调用工具（本地知识库搜索）
    print("\n--- 测试 7 ---")
    print("最终回复:", run_agent("aaa老师住哪里？", tools_schema, available_tools))


def test_agent_chat():
    # 启动聊天循环
    chat_loop(tools_schema, available_tools)

def test_agent_langgraph():
    # 配置信息
    model_config = {
        "model": "deepseek-chat",
        "api_key": "Your api key",
        "api_base": "https://api.deepseek.com"
    }
    # 1. 实例化 Agent
    agent = MyLangGraphAgent(tool_manager, model_config)

    # 2. 交互循环
    print("Agent 已上线！(输入 'exit' 退出)")
    while True:
        user_input = input("\n用户: ")
        if user_input.lower() in ['exit', 'quit', '退出']:
            break

        # 3. 运行并处理流式输出
        for event in agent.run(user_input):
            for node_name, output in event.items():
                print(f"DEBUG: [进入节点 -> {node_name} ]")
                if "messages" in output:
                    last_msg = output["messages"][-1]

                    # 1. 看到 Agent 的决策 (AI 想要做什么)
                    if node_name == "agent":
                        if last_msg.tool_calls:
                            for tool_call in last_msg.tool_calls:
                                print(f"Agent 思考：我需要调用工具 [{tool_call['name']}]，参数: {tool_call['args']}")
                        else:
                            print(f"Agent 最终回复: {last_msg.content}")

                    # 2. 看到工具执行的具体结果
                    elif node_name == "action":
                        # 工具节点可能一次返回多个结果，我们取最新的一个展示
                        print(f"工具执行完毕,执行结果: {last_msg.content}")


if __name__ == "__main__":

    # 直接获取注册好的结果
    tools_schema = tool_manager.tools_schema
    available_tools = tool_manager.available_tools
    # print(f"已自动加载工具: {list(available_tools.keys())}")
    # print(f"已自动加载工具配置: {tools_schema}")

    # 测试单一的工具调用
    # test_single_tool()
    
    # agent正常对话测试
    # test_agent_chat()

    test_agent_langgraph()


