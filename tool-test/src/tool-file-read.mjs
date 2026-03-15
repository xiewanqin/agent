import 'dotenv/config';
import { ChatOpenAI } from '@langchain/openai';
import { tool } from '@langchain/core/tools';
import { HumanMessage, SystemMessage, ToolMessage } from '@langchain/core/messages';
import fs from 'node:fs/promises';
import { z } from 'zod';

// ==================== 第一步：创建 AI 模型 ====================
// 创建一个聊天模型，配置 API 密钥和基础 URL
const model = new ChatOpenAI({ 
  modelName: process.env.MODEL_NAME || "qwen-coder-turbo",
  apiKey: process.env.OPENAI_API_KEY,
  temperature: 0,
  configuration: {
      baseURL: process.env.OPENAI_BASE_URL,
  },
});

// ==================== 第二步：定义工具 ====================
// 创建一个"读取文件"的工具
// 这个工具可以被 AI 模型调用来读取文件内容
const readFileTool = tool(
  // 工具的执行函数：当 AI 调用这个工具时，会执行这个函数
  async ({ filePath }) => {
    const content = await fs.readFile(filePath, 'utf-8');
    console.log(`  [工具调用] read_file("${filePath}") - 成功读取 ${content.length} 字节`);
    return `文件内容:\n${content}`;
  },
  // 工具的元数据：告诉 AI 这个工具是什么、怎么用
  {
    name: 'read_file',  // 工具名称
    description: '用此工具来读取文件内容。当用户要求读取文件、查看代码、分析文件内容时，调用此工具。输入文件路径（可以是相对路径或绝对路径）。',
    // schema: 定义工具的参数结构（就像函数的参数类型定义）
    // 这个 schema 告诉 AI：
    // 1. 这个工具需要什么参数
    // 2. 每个参数是什么类型（字符串、数字等）
    // 3. 每个参数的含义是什么
    schema: z.object({
      // filePath: 参数名，类型是字符串（z.string()）
      // describe(): 告诉 AI 这个参数是干什么用的，帮助 AI 理解如何填写这个参数
      filePath: z.string().describe('要读取的文件路径'),
    }),
  }
);

// 将所有工具放在一个数组中
const tools = [readFileTool];

// ==================== 第三步：给模型绑定工具 ====================
// 这一步很关键！绑定后，AI 模型就知道可以使用哪些工具了
const modelWithTools = model.bindTools(tools);

// ==================== 第四步：准备对话消息 ====================
const messages = [
  // 系统消息：告诉 AI 它的角色和工作方式
  new SystemMessage(`你是一个代码助手，可以使用工具读取文件并解释代码。

工作流程：
1. 用户要求读取文件时，立即调用 read_file 工具
2. 等待工具返回文件内容
3. 基于文件内容进行分析和解释

可用工具：
- read_file: 读取文件内容（使用此工具来获取文件内容）
`),
  // 用户消息：用户的请求
  new HumanMessage('请读取 ./src/tool-file-read.mjs 文件内容并解释代码')
];

// ==================== 第五步：开始对话循环 ====================
console.log('[步骤1] 第一次调用 AI 模型...');
let response = await modelWithTools.invoke(messages);
console.log('[步骤1完成] AI 返回了响应');

// 将 AI 的响应保存到消息历史中
messages.push(response);

// ==================== 第六步：处理工具调用循环 ====================
// 如果 AI 返回了工具调用请求，我们需要执行工具，然后把结果返回给 AI
let maxIterations = 10; // 防止无限循环
let iterationCount = 0;

// 只要 AI 还在请求调用工具，就继续循环
while (response.tool_calls && response.tool_calls.length > 0 && iterationCount < maxIterations) {
  iterationCount++;
  
  console.log(`\n[步骤2-${iterationCount}] 检测到 ${response.tool_calls.length} 个工具调用`);
  
  // ========== 2.1 执行所有工具调用 ==========
  // AI 可能同时请求调用多个工具，我们并行执行它们
  const toolResults = await Promise.all(
    response.tool_calls.map(async (toolCall) => {
      // 根据工具名称找到对应的工具函数
      const tool = tools.find(t => t.name === toolCall.name);
      if (!tool) {
        return `错误: 找不到工具 ${toolCall.name}`;
      }
      
      console.log(`  [执行工具] ${toolCall.name}(${JSON.stringify(toolCall.args)})`);
      try {
        // 执行工具，传入 AI 提供的参数
        const result = await tool.invoke(toolCall.args);
        return result;
      } catch (error) {
        return `错误: ${error.message}`;
      }
    })
  );
  
  // ========== 2.2 将工具执行结果告诉 AI ==========
  // 工具执行完后，需要把结果以 ToolMessage 的形式返回给 AI
  response.tool_calls.forEach((toolCall, index) => {
    messages.push(
      new ToolMessage({
        content: toolResults[index],  // 工具的执行结果
        tool_call_id: toolCall.id,    // 关联到对应的工具调用
      })
    );
  });
  
  // ========== 2.3 再次调用 AI，让它基于工具结果生成回复 ==========
  console.log(`[步骤3-${iterationCount}] 将工具结果发送给 AI，等待最终回复...`);
  response = await modelWithTools.invoke(messages);
  messages.push(response);
  
  // 检查 AI 是否还需要调用更多工具
  if (response.tool_calls && response.tool_calls.length > 0) {
    console.log(`[步骤3-${iterationCount}完成] AI 又返回了 ${response.tool_calls.length} 个工具调用，继续循环...`);
  } else {
    console.log(`[步骤3-${iterationCount}完成] AI 返回了最终回复，退出循环`);
  }
}

// ==================== 第七步：输出最终结果 ====================
if (iterationCount >= maxIterations && response.tool_calls && response.tool_calls.length > 0) {
  console.warn(`\n⚠️ 警告: 达到最大迭代次数 (${maxIterations})，强制退出循环`);
}

console.log('\n========== 最终回复 ==========');
console.log(response.content);
