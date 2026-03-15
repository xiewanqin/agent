# subprocess.Popen vs subprocess.run 对比示例

**主要区别：**
1. `subprocess.run()` - 高级封装，等待进程完成，返回 `CompletedProcess`
2. `subprocess.Popen()` - 底层接口，立即返回，需要手动管理进程

---

## 【方式1】subprocess.run() - 简单场景（推荐）

**特点：**
- 等待进程完成才返回
- 自动管理进程生命周期
- 返回 `CompletedProcess` 对象
- 适合简单的一次性命令执行

### 示例代码

```python
import subprocess

result = subprocess.run(
    ['echo', 'Hello from run()'],
    capture_output=True,  # 捕获输出
    text=True,           # 返回字符串而不是字节
    timeout=5            # 超时设置
)

print(f"返回码: {result.returncode}")
print(f"标准输出: {result.stdout}")
print(f"标准错误: {result.stderr}")
```

**说明：**
- 如果进程还在运行，`run()` 会等待它完成
- 如果超时，会抛出 `TimeoutExpired` 异常

---

## 【方式2】subprocess.Popen() - 灵活控制（高级）

**特点：**
- 立即返回，不等待进程完成
- 返回 `Popen` 对象，可以控制进程
- 需要手动等待进程完成（`wait()` 或 `communicate()`）
- 适合需要实时交互或长时间运行的进程

### 示例代码

```python
import subprocess

process = subprocess.Popen(
    ['echo', 'Hello from Popen()'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print(f"进程已启动，PID: {process.pid}")
print(f"进程是否还在运行: {process.poll() is None}")

# 等待进程完成并获取输出
stdout, stderr = process.communicate()

print(f"返回码: {process.returncode}")
print(f"标准输出: {stdout}")
```

---

## 【方式3】实时输出对比

### subprocess.run() 实时输出

使用 `stdout=None` 继承输出，实时显示：

```python
subprocess.run(
    ['python', '-c', 'import time; [print(f"Line {i}") or time.sleep(0.1) for i in range(5)]'],
    stdout=None,  # 继承父进程输出，实时显示
    stderr=None
)
```

### subprocess.Popen() 实时输出

逐行读取，可以实时显示并捕获：

```python
process = subprocess.Popen(
    ['python', '-c', 'import time; [print(f"Line {i}") or time.sleep(0.1) for i in range(5)]'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1  # 行缓冲
)

# 实时读取并打印
output_lines = []
for line in process.stdout:
    print(f"  [实时] {line.rstrip()}")
    output_lines.append(line)

process.wait()
print(f"\n总共捕获了 {len(output_lines)} 行输出")
```

---

## 【方式4】长时间运行进程对比

### subprocess.run() - 会阻塞直到进程完成

```python
import time
import subprocess

start = time.time()
result = subprocess.run(
    ['python', '-c', 'import time; time.sleep(2); print("Done")'],
    capture_output=True,
    text=True
)
elapsed = time.time() - start
print(f"耗时: {elapsed:.2f} 秒")
print(f"输出: {result.stdout}")
```

### subprocess.Popen() - 立即返回，可以继续做其他事情

```python
import time
import subprocess

start = time.time()
process = subprocess.Popen(
    ['python', '-c', 'import time; time.sleep(2); print("Done")'],
    stdout=subprocess.PIPE,
    text=True
)

print(f"进程已启动，可以继续做其他事情...")
print(f"进程 PID: {process.pid}")

# 等待进程完成
stdout, _ = process.communicate()
elapsed = time.time() - start

print(f"耗时: {elapsed:.2f} 秒")
print(f"输出: {stdout}")
```

---

## 【方式5】进程控制能力对比

### subprocess.Popen() 可以控制进程（终止、发送信号等）

```python
import time
import subprocess

process = subprocess.Popen(
    ['python', '-c', 'import time; [time.sleep(1) or print(i) for i in range(10)]'],
    stdout=subprocess.PIPE,
    text=True
)

print(f"进程已启动: PID {process.pid}")

# 运行 3 秒后终止
time.sleep(3)
print("终止进程...")
process.terminate()  # 发送 SIGTERM

# 等待进程结束
process.wait()
print(f"进程已终止，返回码: {process.returncode}")

# 读取已输出的内容
stdout, _ = process.communicate()
print(f"已输出内容:\n{stdout}")
```

---

## 总结对比表

| 特性                | subprocess.run()     | subprocess.Popen()   |
|---------------------|----------------------|----------------------|
| 返回时机            | 等待进程完成         | 立即返回             |
| 返回值              | CompletedProcess    | Popen 对象           |
| 进程管理            | 自动管理             | 手动管理             |
| 适用场景            | 简单的一次性命令     | 需要控制的复杂场景   |
| 实时输出            | stdout=None          | 逐行读取             |
| 进程控制            | ❌ 不支持            | ✅ 支持（终止等）    |
| 超时设置            | ✅ timeout 参数      | 需要手动实现         |
| 代码复杂度          | 简单                 | 复杂                 |
| 异步支持            | ❌                   | ✅ (asyncio版本)     |

---

## 使用建议

1. **简单命令执行** → 使用 `subprocess.run()`
2. **需要实时输出和捕获** → 使用 `subprocess.Popen() + 逐行读取`
3. **需要控制进程（终止、暂停）** → 使用 `subprocess.Popen()`
4. **异步场景** → 使用 `asyncio.create_subprocess_exec/shell`
