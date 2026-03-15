"""
安装依赖并验证导入
"""
import subprocess
import sys

def install_requirements():
    """安装 requirements.txt 中的依赖"""
    print("正在安装依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装失败: {e}")
        return False

def verify_imports():
    """验证所有导入是否正常"""
    print("\n正在验证导入...")
    imports = [
        "from langchain_openai import ChatOpenAI",
        "from langchain_core.tools import tool",
        "from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage",
        "from pydantic import BaseModel, Field",
        "from dotenv import load_dotenv",
    ]
    
    for import_stmt in imports:
        try:
            exec(import_stmt)
            print(f"✅ {import_stmt}")
        except ImportError as e:
            print(f"❌ {import_stmt}")
            print(f"   错误: {e}")
            return False
    
    print("\n✅ 所有导入验证通过！")
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("LangChain Python 依赖安装和验证")
    print("=" * 50)
    
    if install_requirements():
        verify_imports()
    else:
        print("\n请手动运行: pip install -r requirements.txt")
