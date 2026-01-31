
def calculate_tool_info():
    return {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算简单的数学表达式，如加法、减法、乘法、除法",
            "parameters": {
                "type": "object",
                "properties": {
                    "num1": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "num2": {
                        "type": "number",
                        "description": "第二个数字"
                    },
                    "operation": {
                        "type": "string",
                        "description": "操作符，'add' 表示加法，'subtract' 表示减法,'multiply' 表示乘法,'divide' 表示除法"
                    }
                },
                "required": ["num1", "num2", "operation"]
            }
        }
    }

def calculate(num1, num2, operation):
    if operation == "add":
        return num1 + num2
    elif operation == "subtract":
        return num1 - num2
    elif operation == "multiply":
        return num1 * num2
    elif operation == "divide":
        if num2 == 0:
            return "除数不能为零"
        return num1 / num2
    else:
        return "无效的操作符"