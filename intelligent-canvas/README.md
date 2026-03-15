# 智能可视化画布系统 (Intelligent Canvas System)

基于AI的智能可视化画布系统，支持Agent交互、动态节点编排和流程可视化。

## ✨ 核心功能

### 1. 智能画布核心
- ✅ 基于Web的可视化智能画布
- ✅ 支持Canvas/WebGL高性能渲染
- ✅ 响应式设计，支持高并发、大数据量场景

### 2. Agent交互
- ✅ Agent节点类型支持
- ✅ Agent增强决策功能
- ✅ 智能节点推荐和自动连线

### 3. 动态节点编排
- ✅ 多种节点类型（输入、输出、处理、决策、Agent、RAG、LLM等）
- ✅ 拖拽式节点创建
- ✅ 节点连接和流程可视化
- ✅ 节点编辑和配置

### 4. AI驱动的前端交互
- ✅ AI生成式布局（智能推荐节点位置）
- ✅ 智能推荐节点（基于用户意图）
- ✅ 自动连线功能
- ✅ RAG（检索增强生成）集成
- ✅ LLM API集成和Prompt Engineering支持

### 5. 性能优化
- ✅ Web Workers支持（后台处理大量节点计算）
- ✅ WebAssembly优化方案
- ✅ 虚拟滚动（处理大量节点）
- ✅ Canvas渲染性能优化
- ✅ 高性能模式切换

### 6. 技术栈
- ✅ React 18 + TypeScript
- ✅ React Flow（流程可视化）
- ✅ Zustand（状态管理）
- ✅ OpenAI API集成
- ✅ LangChain支持
- ✅ Web Workers + WebAssembly

## 🚀 快速开始

### 安装依赖

```bash
npm install
```

### 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
VITE_OPENAI_API_KEY=your_openai_api_key_here
VITE_OPENAI_BASE_URL=https://api.openai.com/v1
VITE_MODEL_NAME=gpt-4
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

## 📖 使用指南

### 1. 添加节点
- 从左侧节点面板拖拽节点类型到画布
- 或使用AI工具栏输入需求，让AI智能推荐节点

### 2. 连接节点
- 点击节点的输出端口，拖拽到目标节点的输入端口
- 或使用"智能连线"功能，让AI自动推荐连接

### 3. AI功能
- **智能推荐**：输入你的需求，AI会推荐合适的节点
- **智能布局**：自动优化节点位置，避免重叠
- **智能连线**：基于节点类型和上下文，自动推荐连接关系

### 4. 性能优化
- 切换到"高性能模式"以启用Web Workers和虚拟滚动
- 性能监控面板实时显示FPS、渲染时间等信息

## 🏗️ 项目结构

```
intelligent-canvas/
├── src/
│   ├── components/          # React组件
│   │   ├── Canvas/         # 画布组件
│   │   ├── AIToolbar/      # AI工具栏
│   │   ├── NodePalette/    # 节点面板
│   │   └── PerformanceMonitor/ # 性能监控
│   ├── store/              # 状态管理（Zustand）
│   ├── services/           # 服务层
│   │   └── aiService.ts    # AI服务
│   ├── utils/              # 工具函数
│   │   └── performance.ts  # 性能优化工具
│   ├── workers/            # Web Workers
│   │   └── nodeProcessor.worker.ts
│   ├── types/              # TypeScript类型定义
│   ├── App.tsx             # 主应用组件
│   └── main.tsx            # 入口文件
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## 🎯 技术亮点

### 1. 高性能渲染
- 使用React Flow进行流程可视化
- Canvas/WebGL渲染优化
- Web Workers处理复杂计算
- 虚拟滚动处理大量节点

### 2. AI集成
- OpenAI API集成
- LangChain支持
- RAG（检索增强生成）
- Agent增强决策
- Prompt Engineering

### 3. 现代化技术栈
- React 18 + TypeScript
- Vite构建工具
- Zustand状态管理
- 模块化架构设计

## 🔧 开发计划

- [ ] WebGPU支持
- [ ] 3D画布视图
- [ ] 更多节点类型
- [ ] 节点模板库
- [ ] 导出/导入功能
- [ ] 协作功能
- [ ] 历史版本管理

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！
