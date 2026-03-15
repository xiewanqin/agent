import os
import asyncio
import subprocess
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool

# 1. 读取文件工具
@tool
async def read_file(file_path: str) -> str:
    """读取指定路径的文件内容"""
    try:
        # 使用 asyncio.to_thread() 将同步文件操作转换为异步（Python 3.9+）
        # 如果 Python < 3.9，可以使用: asyncio.get_running_loop().run_in_executor(None, ...)
        def _read():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        content = await asyncio.to_thread(_read)
        print(f'  [工具调用] read_file("{file_path}") - 成功读取 {len(content)} 字节')
        return f'文件内容:\n{content}'
    except Exception as error:
        print(f'  [工具调用] read_file("{file_path}") - 错误: {str(error)}')
        return f'读取文件失败: {str(error)}'


# 2. 写入文件工具
@tool
async def write_file(file_path: str, content: str) -> str:
    """向指定路径写入文件内容，自动创建目录"""
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        # 使用 asyncio.to_thread() 将同步文件操作转换为异步（Python 3.9+）
        def _write():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        await asyncio.to_thread(_write)
        print(f'  [工具调用] write_file("{file_path}") - 成功写入 {len(content)} 字节')
        return f'文件写入成功: {file_path}'
    except Exception as error:
        print(f'  [工具调用] write_file("{file_path}") - 错误: {str(error)}')
        return f'写入文件失败: {str(error)}'


# 3. 执行命令工具（带实时输出）
# echo 在 windows 可能不支持，可以设置 shell: 'powershell.exe'
@tool
async def execute_command(command: str, working_directory: Optional[str] = None) -> str:
    """执行系统命令，支持指定工作目录，实时显示输出"""
    cwd = working_directory or os.getcwd()
    suffix = f' - 工作目录: {working_directory}' if working_directory else ''
    print(f'  [工具调用] execute_command("{command}"){suffix}')
    
    def _run_command():
        # 使用 subprocess.Popen 实现类似 spawn 的行为
        # stdio='inherit' 对应 stdout=None, stderr=None（继承父进程的输出流，实时显示）
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=None,  # None = 继承父进程的 stdout（实时输出，对应 stdio: 'inherit'）
            stderr=None,  # None = 继承父进程的 stderr（实时输出，对应 stdio: 'inherit'）
        )
        
        error_msg = ''
        
        try:
            # 等待进程完成（输出会实时显示在控制台）
            return_code = process.wait()
            
            if return_code == 0:
                print(f'  [工具调用] execute_command("{command}") - 执行成功')
                cwd_info = (
                    f'\n\n重要提示：命令在目录 "{working_directory}" 中执行成功。'
                    f'如果需要在这个项目目录中继续执行命令，请使用 workingDirectory: "{working_directory}" 参数，不要使用 cd 命令。'
                    if working_directory
                    else ''
                )
                return f'命令执行成功: {command}{cwd_info}'
            else:
                print(f'  [工具调用] execute_command("{command}") - 执行失败，退出码: {return_code}')
                error_info = f'\n错误: {error_msg}' if error_msg else ''
                return f'命令执行失败，退出码: {return_code}{error_info}'
        except Exception as error:
            error_msg = str(error)
            print(f'  [工具调用] execute_command("{command}") - 错误: {error_msg}')
            return_code = process.returncode if process.poll() is not None else None
            return f'命令执行失败，退出码: {return_code if return_code is not None else "未知"}\n错误: {error_msg}'
    
    # 在异步上下文中运行同步函数
    return await asyncio.to_thread(_run_command)


# 4. 列出目录内容工具
@tool
async def list_directory(directory_path: str) -> str:
    """列出指定目录下的所有文件和文件夹"""
    try:
        # 使用 asyncio.to_thread() 将同步目录操作转换为异步（Python 3.9+）
        files = await asyncio.to_thread(os.listdir, directory_path)
        
        print(f'  [工具调用] list_directory("{directory_path}") - 找到 {len(files)} 个项目')
        return f'目录内容:\n' + '\n'.join([f'- {f}' for f in files])
    except Exception as error:
        print(f'  [工具调用] list_directory("{directory_path}") - 错误: {str(error)}')
        return f'列出目录失败: {str(error)}'


# 导出所有工具
__all__ = ['read_file', 'write_file', 'execute_command', 'list_directory']
