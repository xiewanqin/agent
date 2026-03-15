import os
import asyncio
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
import colorama
from colorama import Fore, Back, Style
from langchain.agents import create_agent

# 导入工具
from python_tool_good import read_file, write_file, execute_command, list_directory

# 初始化 colorama
colorama.init(autoreset=True)

# 加载环境变量
load_dotenv()

# 初始化模型
model = init_chat_model(
    "openai:qwen-plus",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    base_url=os.getenv("OPENAI_BASE_URL"),
)

# 工具列表
tools = [
    read_file,
    write_file,
    execute_command,
    list_directory,
]

system_prompt = f"""你是一个项目管理助手，使用工具完成任务。

当前工作目录: {os.getcwd()}

工具：
1. read_file: 读取文件
2. write_file: 写入文件
3. execute_command: 执行命令（支持 workingDirectory 参数）
4. list_directory: 列出目录

重要规则 - execute_command：
- workingDirectory 参数会自动切换到指定目录
- 当使用 workingDirectory 时，绝对不要在 command 中使用 cd
- 错误示例: {{ command: "cd react-todo-app && pnpm install", workingDirectory: "react-todo-app" }}
这是错误的！因为 workingDirectory 已经在 react-todo-app 目录了，再 cd react-todo-app 会找不到目录
- 正确示例: {{ command: "pnpm install", workingDirectory: "react-todo-app" }}
这样就对了！workingDirectory 已经切换到 react-todo-app，直接执行命令即可

重要规则 - write_file：
- 当写入 React 组件文件（如 App.tsx）时，如果存在对应的 CSS 文件（如 App.css），在其他 import 语句后加上这个 css 的导入
"""

# Agent 执行函数
graph = create_agent(
    model=model,
    tools=tools,
    system_prompt=system_prompt,
)


# 案例查询
case1 = """创建一个功能丰富的 React TodoList 应用：

1. 创建项目：使用命令 echo -e '\\n\\n' | pnpm create vite react-todo-app --template react-ts 创建项目（使用 echo 提供输入以避免交互式提示）
2. 修改 src/App.tsx，实现完整功能的 TodoList（必须使用 write_file 工具写入完整的代码，不要只修改部分内容）：
 - 添加、删除、编辑、标记完成
 - 分类筛选（全部/进行中/已完成）
 - 统计信息显示
 - localStorage 数据持久化
3. 添加复杂样式：
 - 渐变背景（蓝到紫）
 - 卡片阴影、圆角
 - 悬停效果
4. 添加动画：
 - 添加/删除时的过渡动画
 - 使用 CSS transitions
5. 列出目录确认

注意：使用 pnpm，功能要完整，样式要美观，要有动画效果

之后在 react-todo-app 项目中：
1. 使用 pnpm install 安装依赖
2. 使用 pnpm run dev 启动服务器
"""


async def main():
  print('[开始] 使用 create_agent 执行任务...')
  inputs = {
      "messages": [
          {"role": "user", "content": case1}
      ]
  }
  print(Back.GREEN + '⏳ 正在等待 AI 思考...' + Style.RESET_ALL)
  result = await graph.ainvoke(inputs)
  print(result)


if __name__ == "__main__":
  asyncio.run(main())
