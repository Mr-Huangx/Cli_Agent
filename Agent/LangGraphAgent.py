import os
from typing import Annotated, List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.tools import StructuredTool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver


# 定义状态类型
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

class MyLangGraphAgent:
    def __init__(self, tool_manager, model_config):
        self.tool_manager = tool_manager
        
        # 1. 转换并包装工具
        self.langchain_tools = self._setup_tools()
        
        # 2. 初始化 LLM 并绑定工具
        self.llm = ChatOpenAI(
            model=model_config.get("model", "deepseek-chat"),
            openai_api_key=model_config.get("api_key"),
            openai_api_base=model_config.get("api_base")
        ).bind_tools(self.langchain_tools)
        
        # 3. 构建图
        self.app = self._build_graph()

    def _setup_tools(self):
        langchain_tools = []
        for func_name, func_obj in self.tool_manager.available_tools.items():
            tool_desc = next(
                (t['function']['description'] for t in self.tool_manager.tools_schema 
                 if t['function']['name'] == func_name), "无描述"
            )
            lc_tool = StructuredTool.from_function(
                func=func_obj,
                name=func_name,
                description=tool_desc
            )
            langchain_tools.append(lc_tool)
        return langchain_tools

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        sysytem_prompt = """你是一个具备多项工具能力的智能助手,同时你拥有一些实时工具调用能力的助手。你的知识由两部分组成：1. 你的内置训练数据（截止日期前的通用知识）；2. 工具提供的外部实时数据（当前事实）。
    请根据用户的提问回答问题。你的回答请严格遵守以下思维链路CoT：
1. 先查后说。根据用户的问题首先判断使用工具是否可以回答用户的问题。如果可以，根据用户的问题调用对应的工具回答问题。如果使用工具之后不能回答用户的问题，根据用户的问题直接根据内置训练数据回答用户的问题。
2. 知识库优先准则。
3. 处理工具结果。获取工具返回的信息后，请结合信息给出准确回答。如果工具没查到，请如实告知用户，不要胡编乱造。
4. 回答风格。简洁、直接。如果通过工具查到了信息，请注明“根据已有记录显示...”。
5. 严禁“马后炮”。严禁先给出答案再调用工具验证。如果你认为需要工具支持，请直接生成工具调用指令，不要在指令前输出任何正文。
    """

        # 内部节点定义
        def call_model(state: AgentState):
            messages = state['messages']
            if not any(isinstance(msg, SystemMessage) for msg in messages):
                messages = [SystemMessage(content=sysytem_prompt)] + messages
            return {"messages": [self.llm.invoke(messages)]}

        def should_continue(state: AgentState):
            last_message = state['messages'][-1]
            return "continue" if last_message.tool_calls else "end"

        # 添加节点
        workflow.add_node("agent", call_model)
        workflow.add_node("action", ToolNode(self.langchain_tools))

        # 编排边
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent", 
            should_continue, 
            {"continue": "action", "end": END}
        )
        workflow.add_edge("action", "agent")

        # 在 build_graph 之前
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory) 

    def run(self, prompt: str):
        """流式运行接口"""
        inputs = {"messages": [HumanMessage(content=prompt)]}
        # 使用流式输出方便观察过程
        for event in self.app.stream(inputs, config={"configurable": {"thread_id": "1"}}):
            yield event