

def get_weather_tool_info():
    return {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询天气的城市名称,例如：北京、上海",
                    },
                },
                "required": ["city"],
            }
        }
    }

def get_weather(city: str):
    """模拟天气数据，在实际使用过程中，这里需要替换为Requests去请求天气的API"""
    weather_data = {
        "北京" :"晴天",
        "上海" :"多云",
        "广州" :"阴",
        "深圳" :"晴",
    }
    return weather_data.get(city, f"未知城市{city}的天气")


