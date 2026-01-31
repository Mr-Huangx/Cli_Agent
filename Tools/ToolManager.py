class ToolManager:
    def __init__(self):
        self.tools_schema = []
        self.available_tools = {}

    def register_tool(self, schema):
        """这是一个装饰器，用于自动注册工具"""
        def decorator(func):
            # 1. 将函数存入执行字典
            self.available_tools[func.__name__] = func
            # 2. 将配置信息存入 Schema 列表
            self.tools_schema.append(schema)
            return func
        return decorator

# 初始化一个全局管理器
tool_manager = ToolManager()