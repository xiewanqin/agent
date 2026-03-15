// 节点类型定义
export interface Node {
  id: string
  type: NodeType
  position: { x: number; y: number }
  data: NodeData
  width?: number
  height?: number
  style?: NodeStyle
}

export type NodeType = 
  | 'input' 
  | 'output' 
  | 'process' 
  | 'decision' 
  | 'agent' 
  | 'rag' 
  | 'llm' 
  | 'custom'

export interface NodeData {
  label: string
  description?: string
  config?: Record<string, any>
  aiGenerated?: boolean
  aiSuggestion?: string
}

export interface NodeStyle {
  backgroundColor?: string
  borderColor?: string
  borderWidth?: number
  borderRadius?: number
  fontSize?: number
  color?: string
}

// 连接线定义
export interface Edge {
  id: string
  source: string
  target: string
  sourceHandle?: string | null
  targetHandle?: string | null
  animated?: boolean
  style?: EdgeStyle
  aiGenerated?: boolean
}

export interface EdgeStyle {
  stroke?: string
  strokeWidth?: number
  strokeDasharray?: string
}

// 画布状态
export interface CanvasState {
  nodes: Node[]
  edges: Edge[]
  selectedNodes: string[]
  selectedEdges: string[]
  viewport: {
    x: number
    y: number
    zoom: number
  }
  aiEnabled: boolean
  performanceMode: 'normal' | 'high-performance'
}

// AI相关类型
export interface AISuggestion {
  type: 'node' | 'edge' | 'layout'
  suggestion: string
  confidence: number
  data?: Partial<Node> | Partial<Edge>
}

export interface LLMConfig {
  apiKey: string
  baseURL: string
  model: string
  temperature?: number
  maxTokens?: number
}

// RAG相关
export interface RAGContext {
  query: string
  documents: string[]
  embeddings?: number[][]
  relevanceScore?: number
}

// Agent相关
export interface AgentConfig {
  name: string
  description: string
  tools: string[]
  prompt: string
  model?: string
}
