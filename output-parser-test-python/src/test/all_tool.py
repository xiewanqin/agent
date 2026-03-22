import os
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# 工具函数


@tool
async def read_file(file_path: str) -> str:
  """读取指定路径的文件内容"""
  try:
    # 使用 asyncio 的子进程执行文件读取（模拟异步）
    content = await asyncio.get_event_loop().run_in_executor(
        None, lambda: open(file_path, 'r', encoding='utf-8').read()
    )
    print(f"  [工具调用] read_file(\"{file_path}\") - 成功读取 {len(content)} 字节")
    return f"文件内容:\n{content}"
  except Exception as e:
    print(f"  [工具调用] read_file(\"{file_path}\") - 错误: {str(e)}")
    return f"读取文件失败: {str(e)}"


@tool
async def write_file(file_path: str, content: str) -> str:
  """向指定路径写入文件内容，自动创建目录"""
  try:
    # 确保目录存在
    directory = os.path.dirname(file_path)
    if directory:
      os.makedirs(directory, exist_ok=True)

    # 使用 asyncio 的 executor 写入文件
    await asyncio.get_event_loop().run_in_executor(
        None, lambda: open(file_path, 'w', encoding='utf-8').write(content)
    )
    print(f"  [工具调用] write_file(\"{file_path}\") - 成功写入 {len(content)} 字节")
    return f"文件写入成功: {file_path}"
  except Exception as e:
    print(f"  [工具调用] write_file(\"{file_path}\") - 错误: {str(e)}")
    return f"写入文件失败: {str(e)}"


# @tool
# async def execute_command(command: str, working_directory: Optional[str] = None) -> str:
#   """执行系统命令，支持指定工作目录，实时显示输出"""
#   cwd = working_directory or os.getcwd()
#   suffix = f" - 工作目录: {working_directory}" if working_directory else ""
#   print(f'  [工具调用] execute_command("{command}"){suffix}')

#   process = None
#   try:
#     # 创建子进程（create_subprocess_shell 默认在 shell 中执行，无需 shell=True）
#     process = await asyncio.create_subprocess_shell(
#         command,
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE,
#         cwd=cwd,
#     )

#     # 实时读取输出
#     stdout_lines = []
#     stderr_lines = []

#     async def read_stream(stream, lines_list):
#       while True:
#         line = await stream.readline()
#         if not line:
#           break
#         decoded_line = line.decode('utf-8', errors='ignore').rstrip()
#         lines_list.append(decoded_line)
#         print(decoded_line)

#     # 同时读取 stdout 和 stderr
#     await asyncio.gather(
#         read_stream(process.stdout, stdout_lines),
#         read_stream(process.stderr, stderr_lines)
#     )

#     # 等待进程结束
#     return_code = await process.wait()

#     if return_code == 0:
#       print(f'  [工具调用] execute_command("{command}") - 执行成功')
#       cwd_info = (f"\n\n重要提示：命令在目录 \"{working_directory}\" 中执行成功。"
#                   f"如果需要在这个项目目录中继续执行命令，"
#                   f"请使用 working_directory: \"{working_directory}\" 参数，不要使用 cd 命令。"
#                   if working_directory else "")
#       output = '\n'.join(stdout_lines)
#       return f"命令执行成功: {command}\n{output}{cwd_info}"
#     else:
#       print(f'  [工具调用] execute_command("{command}") - 执行失败，退出码: {return_code}')
#       stdout_str = '\n'.join(stdout_lines)
#       stderr_str = '\n'.join(stderr_lines)
#       parts = [f"命令执行失败，退出码: {return_code}"]
#       if stdout_str:
#         parts.append(f"stdout:\n{stdout_str}")
#       if stderr_str:
#         parts.append(f"stderr:\n{stderr_str}")
#       return '\n'.join(parts)

#   except Exception as e:
#     if process is not None:
#       try:
#         process.terminate()
#         await process.wait()
#       except Exception:
#         pass
#     print(f'  [工具调用] execute_command("{command}") - 错误: {str(e)}')
#     return f"执行命令失败: {str(e)}"

@tool
async def execute_command(command: str, working_directory: str | None = None) -> str:
  """执行系统命令，支持指定工作目录，实时显示输出"""
  cwd = working_directory or os.getcwd()
  print(
      f'  [工具调用] execute_command("{command}"){
          f" - 工作目录: {working_directory}" if working_directory else ""}')

  def _run():
    # 方式1: 使用 subprocess.run()，不指定 stdout/stderr 表示继承（类似 stdio: 'inherit'）
    # 输出会实时显示在控制台
    return subprocess.run(
        command,
        shell=True,
        cwd=cwd,
        # stdout=None 和 stderr=None 表示继承父进程的标准输出/错误流
        # 这样输出会实时显示在控制台，类似 Node.js 的 stdio: 'inherit'
        stdout=None,  # None = 继承父进程的 stdout（实时输出）
        stderr=None,  # None = 继承父进程的 stderr（实时输出）
    )

  result = await asyncio.to_thread(_run)
  if result.returncode == 0:
    print(f'  [工具调用] execute_command("{command}") - 执行成功')
    cwd_info = (
        f'\n\n重要提示：命令在目录 "{working_directory}" 中执行成功。如果需要在这个项目目录中继续执行命令，请使用 workingDirectory: "{working_directory}" 参数，不要使用 cd 命令。'
        if working_directory
        else ''
    )
    return f'命令执行成功: {command}{cwd_info}'
  else:
    print(f'  [工具调用] execute_command("{command}") - 执行失败，退出码: {result.returncode}')
    return f'命令执行失败，退出码: {result.returncode}'


@tool
async def list_directory(directory_path: str) -> str:
  """列出指定目录下的所有文件和文件夹"""
  try:
    # 使用 asyncio 的 executor 读取目录
    files = await asyncio.get_event_loop().run_in_executor(
        None, lambda: os.listdir(directory_path)
    )

    # 获取详细信息
    items = []
    for f in sorted(files):
      full_path = os.path.join(directory_path, f)
      if os.path.isdir(full_path):
        items.append(f"[DIR]  {f}")
      else:
        size = os.path.getsize(full_path)
        items.append(f"[FILE] {f} ({size} bytes)")

    print(f"  [工具调用] list_directory(\"{directory_path}\") - 找到 {len(files)} 个项目")
    return f"目录内容:\n" + "\n".join(items)
  except Exception as e:
    print(f"  [工具调用] list_directory(\"{directory_path}\") - 错误: {str(e)}")
    return f"列出目录失败: {str(e)}"
