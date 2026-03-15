import { tool } from '@langchain/core/tools';
import fs from 'node:fs/promises';
import { z } from 'zod';

const readFileTool = tool(
  async ({ filePath }) => {
    try {
      const content = await fs.readFile(filePath, 'utf-8');
      console.log(`  [工具调用] read_file("${filePath}") - 成功读取 ${content.length} 字节`);
      return `文件内容:\n${content}`;
    } catch (error) {
      console.log(`  [工具调用] read_file("${filePath}") - 错误: ${error.message}`);
      return `读取文件失败: ${error.message}`;
    }
  },
  {
    name: 'read_file',
    description: '用此工具来读取文件内容。当用户要求读取文件、查看代码、分析文件内容时，调用此工具。输入文件路径（可以是相对路径或绝对路径）。',
    schema: z.object({
      filePath: z.string().describe('要读取的文件路径'),
    }),
  }
);

const writeFileTool = tool(
  async ({ filePath, content }) => {
    try {
      const dir = path.dirname(filePath);
      await fs.mkdir(dir, { recursive: true });
      await fs.writeFile(filePath, content, 'utf-8');
      console.log(`  [工具调用] write_file("${filePath}") - 成功写入 ${content.length} 字节`);
      return `文件写入成功: ${filePath}`;
    } catch (error) {
      console.log(`  [工具调用] write_file("${filePath}") - 错误: ${error.message}`);
      return `写入文件失败: ${error.message}`;
    }
  },
  {
    name: 'write_file',
    description: '用此工具来写入文件内容。当用户要求写入文件、修改代码、保存文件内容时，调用此工具。输入文件路径（可以是相对路径或绝对路径）和要写入的文件内容。',
    schema: z.object({
      filePath: z.string().describe('要写入的文件路径'),
      content: z.string().describe('要写入的文件内容'),
    }),
  }
);

const executeCommandTool = tool(
  async ({ command, workingDirectory }) => {
    const cwd = workingDirectory || process.cwd();
    console.log(`  [工具调用] execute_command("${command}")${workingDirectory ? ` - 工作目录: ${workingDirectory}` : ''}`);
    try {
      const [cmd, ...args] = command.split(' ');
      const result = await spawn(cmd, args, { stdio: 'inherit', shell: true });
      return `命令执行成功: ${result.stdout}`;
    } catch (error) {
      return `命令执行失败: ${error.message}`;
    }
  },
  {
    name: 'execute_command',
    description: '用此工具来执行系统命令。当用户要求执行系统命令、运行脚本、执行命令行操作时，调用此工具。输入要执行的命令。',
    schema: z.object({
      command: z.string().describe('要执行的命令'),
    }),
  }
);

export { readFileTool, writeFileTool };