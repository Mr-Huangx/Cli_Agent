from openai import OpenAI
import json
from Memory.ShortTermMemory import short_term_memory

client = OpenAI(
        api_key="Your Deepseek API Key",
        base_url="https://api.deepseek.com",
    )

def run_agent(user_input, tools_schema, available_tools, model_name = "deepseek-chat"):
    messages = [
        {"role": "system", "content": "你是一个有用的AI助手。如果用户问的问题需要查询实时信息（时间、天气），请使用工具。"},
        {"role": "user", "content": user_input},
    ]

    print(f"用户请求：{user_input}")

    # --- 进入 ReAct 循环 ---
    while True:
        # 获取 LLM 的回复消息
        response = client.chat.completions.create(
            model=model_name, # 或者 "deepseek-reasoner"
            messages=messages,
            tools=tools_schema, 
        )

        assistant_msg = response.choices[0].message
        print(f"LLM回复：{assistant_msg.content}")

        # 判断 LLM 是否想要调用工具 (Tool Calls)
        if assistant_msg.tool_calls:
            print(f"Agent 思考: 我需要调用工具 -> {assistant_msg.tool_calls[0].function.name}")
            # 必须把 LLM "想调用工具" 的这条意图加入历史，否则它会忘记
            messages.append(assistant_msg)

            # 执行工具
            for tool_call in assistant_msg.tool_calls:
                # 解析函数名和参数
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)

                # 从我们的函数字典里找到对应的 Python 函数
                func_to_call = available_tools[tool_name]

                try:
                    func_result = func_to_call(**tool_args)
                    print(f"工具 {tool_name} 返回: {func_result}")

                except Exception as e:
                    func_result = f"工具执行出错：{str(e)}"

                messages.append({
                    "role": "tool",
                    "content": str(func_result),
                    "tool_call_id": tool_call.id,
                })
        else:
            # 如果 LLM 觉得不需要调用工具，直接返回它的回复
            return assistant_msg.content

def chat_loop(tools_schema, available_tools, model_name = "deepseek-chat"):
    # System Prompt 只需要初始化一次
    short_term_memory = [
        {"role": "system", "content": "你是一个有用的AI助手。如果用户问的问题需要查询实时信息（时间、天气、简单计算），请使用工具。"}
    ]

    print("Agent 已启动！(输入 'exit' 退出)")
    print("-" * 50)

    while True:
        user_input = input("用户: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Agent: 再见！")
            break

        # 把用户输入和 Agent 回复加入短期记忆
        short_term_memory.append({"role": "user", "content": user_input})

        # 调用 LLM （使用while开启自循环模式）
        while True:
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=short_term_memory,
                    tools=tools_schema
                )
            except Exception as e:
                print(f"❌ API 请求出错: {e}")
                continue

            assistant_msg = response.choices[0].message

            # 把 LLM 的回复加入短期记忆
            short_term_memory.append(assistant_msg)
            # print(f"LLM回复：{assistant_msg.content}")
            # 判断 LLM 是否想要调用工具 (Tool Calls)
            if assistant_msg.tool_calls:
                print(f"Agent 思考: 我需要调用工具 -> {assistant_msg.tool_calls[0].function.name}")

                # 执行工具
                for tool_call in assistant_msg.tool_calls:
                    # 解析函数名和参数
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)

                    # 从我们的函数字典里找到对应的 Python 函数
                    func_to_call = available_tools[tool_name]

                    try:
                        func_result = func_to_call(**tool_args)
                        print(f"工具 {tool_name} 返回: {func_result}")

                    except Exception as e:
                        func_result = f"工具执行出错：{str(e)}"

                    # 把工具执行结果加入短期记忆
                    short_term_memory.append({
                        "role": "tool",
                        "content": str(func_result),
                        "tool_call_id": tool_call.id,
                    })

            else:
                # 如果 LLM 觉得不需要调用工具，直接打印它的回复
                print(f"Agent 回复: {assistant_msg.content}")
                break #跳出自循环，等待用户下一次输入
