// 应用常量配置

export const NODE_DEFAULT_SIZE = {
  width: 150,
  height: 60,
}

export const CANVAS_CONFIG = {
  minZoom: 0.1,
  maxZoom: 4,
  defaultZoom: 1,
  gridSize: 20,
}

export const PERFORMANCE_THRESHOLDS = {
  excellent: 55, // FPS >= 55 为优秀
  good: 30, // FPS >= 30 为良好
  maxNodesForNormalMode: 100, // 普通模式最大节点数
  maxNodesForHighPerformanceMode: 1000, // 高性能模式最大节点数
}

export const AI_CONFIG = {
  defaultTemperature: 0.7,
  defaultMaxTokens: 1000,
  suggestionLimit: 5, // 每次最多推荐5个节点
}

export const NODE_COLORS = {
  input: { bg: '#e3f2fd', border: '#2196f3' },
  output: { bg: '#f3e5f5', border: '#9c27b0' },
  process: { bg: '#e8f5e9', border: '#4caf50' },
  decision: { bg: '#fff3e0', border: '#ff9800' },
  agent: { bg: '#e1f5fe', border: '#00bcd4' },
  rag: { bg: '#fce4ec', border: '#e91e63' },
  llm: { bg: '#f1f8e9', border: '#8bc34a' },
  custom: { bg: '#ffffff', border: '#757575' },
}
