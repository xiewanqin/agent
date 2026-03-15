import { LLMConfig, Node, Edge, AISuggestion, RAGContext, AgentConfig } from '@/types'
import OpenAI from 'openai'

class AIService {
  private client: OpenAI | null = null
  private config: LLMConfig | null = null

  initialize(config: LLMConfig) {
    this.config = config
    this.client = new OpenAI({
      apiKey: config.apiKey,
      baseURL: config.baseURL,
      dangerouslyAllowBrowser: true, // ⚠️ 警告：仅在开发环境使用，生产环境应使用后端代理
    })
  }

  async generateNodeSuggestions(
    context: { nodes: Node[]; edges: Edge[]; userIntent?: string }
  ): Promise<AISuggestion[]> {
    if (!this.client || !this.config) {
      throw new Error('AI Service not initialized')
    }

    const prompt = `基于以下画布上下文，推荐合适的节点：
画布节点: ${JSON.stringify(context.nodes.map(n => ({ type: n.type, label: n.data.label })))}
连接关系: ${JSON.stringify(context.edges.map(e => ({ from: e.source, to: e.target })))}
用户意图: ${context.userIntent || '无'}

请推荐3-5个合适的节点，包括节点类型、标签和位置建议。返回JSON格式：
[
  {
    "type": "node",
    "suggestion": "建议添加一个数据处理节点",
    "confidence": 0.8,
    "data": {
      "type": "process",
      "label": "数据处理",
      "position": {"x": 200, "y": 300}
    }
  }
]`

    try {
      const completion = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: '你是一个智能画布助手，帮助用户设计工作流程。',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: this.config.temperature || 0.7,
        max_tokens: this.config.maxTokens || 1000,
      })

      const content = completion.choices[0]?.message?.content || '[]'
      const suggestions = JSON.parse(content) as AISuggestion[]
      return suggestions
    } catch (error) {
      console.error('AI suggestion error:', error)
      return []
    }
  }

  async suggestConnections(
    nodes: Node[],
    sourceNodeId: string
  ): Promise<AISuggestion[]> {
    if (!this.client || !this.config) {
      throw new Error('AI Service not initialized')
    }

    const sourceNode = nodes.find((n) => n.id === sourceNodeId)
    if (!sourceNode) return []

    const prompt = `节点 "${sourceNode.data.label}" (类型: ${sourceNode.type}) 应该连接到哪些节点？
可用节点: ${nodes
      .filter((n) => n.id !== sourceNodeId)
      .map((n) => `${n.data.label} (${n.type})`)
      .join(', ')}

返回JSON格式的连接建议。`

    try {
      const completion = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: '你是一个智能画布助手，帮助用户建立节点之间的连接关系。',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: 0.5,
      })

      const content = completion.choices[0]?.message?.content || '[]'
      return JSON.parse(content) as AISuggestion[]
    } catch (error) {
      console.error('Connection suggestion error:', error)
      return []
    }
  }

  async autoLayout(nodes: Node[], edges: Edge[]): Promise<Node[]> {
    if (!this.client || !this.config) {
      throw new Error('AI Service not initialized')
    }

    // 使用AI生成智能布局
    const prompt = `为以下节点生成最优布局：
节点: ${JSON.stringify(nodes.map(n => ({ id: n.id, type: n.type, label: n.data.label })))}
连接: ${JSON.stringify(edges.map(e => ({ from: e.source, to: e.target })))}

返回每个节点的新位置坐标，使用力导向布局算法优化。`

    try {
      const completion = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: '你是一个布局算法专家，擅长优化节点布局。',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: 0.3,
      })

      const content = completion.choices[0]?.message?.content || '{}'
      const layout = JSON.parse(content) as Record<string, { x: number; y: number }>

      return nodes.map((node) => ({
        ...node,
        position: layout[node.id] || node.position,
      }))
    } catch (error) {
      console.error('Auto layout error:', error)
      return nodes
    }
  }

  async ragQuery(context: RAGContext): Promise<string> {
    if (!this.client || !this.config) {
      throw new Error('AI Service not initialized')
    }

    const prompt = `基于以下文档上下文回答问题：
查询: ${context.query}
文档: ${context.documents.join('\n\n')}

请提供准确的答案。`

    try {
      const completion = await this.client.chat.completions.create({
        model: this.config.model,
        messages: [
          {
            role: 'system',
            content: '你是一个RAG助手，基于提供的文档回答问题。',
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: 0.5,
      })

      return completion.choices[0]?.message?.content || ''
    } catch (error) {
      console.error('RAG query error:', error)
      return ''
    }
  }

  async agentDecision(agentConfig: AgentConfig, context: string): Promise<string> {
    if (!this.client || !this.config) {
      throw new Error('AI Service not initialized')
    }

    const prompt = `${agentConfig.prompt}

上下文: ${context}

可用工具: ${agentConfig.tools.join(', ')}

请做出决策并说明理由。`

    try {
      const completion = await this.client.chat.completions.create({
        model: agentConfig.model || this.config.model,
        messages: [
          {
            role: 'system',
            content: `你是 ${agentConfig.name}: ${agentConfig.description}`,
          },
          {
            role: 'user',
            content: prompt,
          },
        ],
        temperature: 0.7,
      })

      return completion.choices[0]?.message?.content || ''
    } catch (error) {
      console.error('Agent decision error:', error)
      return ''
    }
  }
}

export const aiService = new AIService()
