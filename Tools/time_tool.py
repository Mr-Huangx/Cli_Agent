import datetime

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

def get_current_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")