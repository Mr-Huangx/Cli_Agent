from openai import OpenAI
import json
from Memory.ShortTermMemory import short_term_memory

client = OpenAI(
        api_key="Your Deepseek API Key",
        base_url="https://api.deepseek.com",
    )

sysytem_prompt = """你是一个具备多项工具能力的智能助手,同时你拥有一些实时工具调用能力的助手。你的知识由两部分组成：1. 你的内置训练数据（截止日期前的通用知识）；2. 工具提供的外部实时数据（当前事实）。
    请根据用户的提问回答问题。你的回答请严格遵守以下思维链路CoT：
1. 先查后说。根据用户的问题首先判断使用工具是否可以回答用户的问题。如果可以，根据用户的问题调用对应的工具回答问题。如果使用工具之后不能回答用户的问题，根据用户的问题直接根据内置训练数据回答用户的问题。
2. 知识库优先准则。
3. 处理工具结果。获取工具返回的信息后，请结合信息给出准确回答。如果工具没查到，请如实告知用户，不要胡编乱造。
4. 回答风格。简洁、直接。如果通过工具查到了信息，请注明“根据已有记录显示...”。
5. 严禁“马后炮”。严禁先给出答案再调用工具验证。如果你认为需要工具支持，请直接生成工具调用指令，不要在指令前输出任何正文。
    """

def run_agent(user_input, tools_schema, available_tools, model_name = "deepseek-chat"):
    messages = [
        {"role": "system", "content": sysytem_prompt},
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
        {"role": "system", "content": sysytem_prompt}
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
