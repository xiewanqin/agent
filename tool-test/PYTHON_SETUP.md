# Python 版本搭建指南

## 📋 步骤概览

1. 创建 Python 虚拟环境
2. 安装依赖包
3. 创建项目结构
4. 配置环境变量
5. 编写 Python 代码

---

## 🚀 详细步骤

### 步骤 1: 创建 Python 虚拟环境

```bash
# 进入项目目录
cd /Users/xiewq/web/agent/tool-test

# 创建虚拟环境（Python 3.8+）
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### 步骤 2: 安装依赖包

创建 `requirements.txt` 文件，然后安装：

```bash
pip install langchain-openai langchain-core python-dotenv pydantic
```

或者直接安装：
```bash
pip install langchain-openai langchain-core python-dotenv pydantic
```

### 步骤 3: 创建项目结构

```
tool-test/
├── venv/              # 虚拟环境（自动生成）
├── .env               # 环境变量（已存在）
├── requirements.txt  # Python 依赖（需要创建）
├── src/
│   └── tool_file_read.py  # Python 版本的主文件（需要创建）
└── PYTHON_SETUP.md   # 本指南
```

### 步骤 4: 配置环境变量

`.env` 文件已经存在，确保包含：
```
OPENAI_API_KEY=sk-22a10250468548c7b644da4fd28e754f
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-coder-turbo
```

### 步骤 5: 创建 Python 代码文件

创建 `src/tool_file_read.py`（参考下面的代码模板）

---

## 📦 依赖包说明

| JavaScript 包 | Python 包 | 作用 |
|--------------|----------|------|
| `@langchain/openai` | `langchain-openai` | OpenAI 兼容的聊天模型 |
| `@langchain/core` | `langchain-core` | LangChain 核心功能（工具、消息等） |
| `zod` | `pydantic` | 数据验证和类型定义 |
| `dotenv` | `python-dotenv` | 读取 .env 文件 |
| `fs/promises` | `pathlib` 或 `open()` | 文件操作（Python 内置） |

---

## 🔄 JavaScript vs Python 语法对比

### 导入模块
```javascript
// JavaScript
import { ChatOpenAI } from '@langchain/openai';
import { tool } from '@langchain/core/tools';
import { z } from 'zod';
```

```python
# Python
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from pydantic import BaseModel, Field
```

### 环境变量
```javascript
// JavaScript
import 'dotenv/config';
const apiKey = process.env.OPENAI_API_KEY;
```

```python
# Python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
```

### 异步函数
```javascript
// JavaScript
async function readFile(filePath) {
  const content = await fs.readFile(filePath, 'utf-8');
  return content;
}
```

```python
# Python
async def read_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content
```

### 工具定义
```javascript
// JavaScript
const tool = tool(async ({ filePath }) => {
  // ...
}, {
  name: 'read_file',
  schema: z.object({
    filePath: z.string()
  })
});
```

```python
# Python
@tool
def read_file(file_path: str) -> str:
    """读取文件内容"""
    # ...
    return content
```

---

## ✅ 检查清单

完成以下步骤后，打勾确认：

- [ ] 创建了虚拟环境 `venv`
- [ ] 激活了虚拟环境
- [ ] 安装了所有依赖包
- [ ] 创建了 `requirements.txt`
- [ ] `.env` 文件配置正确
- [ ] 创建了 `src/tool_file_read.py`
- [ ] 测试运行成功

---

## 🧪 测试运行

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 运行 Python 脚本
python src/tool_file_read.py
```

---

## 💡 提示

1. **虚拟环境**：每次开发前记得激活虚拟环境
2. **依赖管理**：使用 `pip freeze > requirements.txt` 导出依赖
3. **Python 版本**：建议使用 Python 3.8 或更高版本
4. **异步支持**：Python 的异步需要使用 `asyncio.run()` 或 `await`
