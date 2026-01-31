import datetime
from Tools.ToolManager import tool_manager


def time_tool_info():
    return {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前时间",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            }
        }
    }

@tool_manager.register_tool(time_tool_info())
def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")