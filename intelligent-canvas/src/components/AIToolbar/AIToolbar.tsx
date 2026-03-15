import React, { useState } from 'react'
import { useCanvasStore } from '@/store/canvasStore'
import { aiService } from '@/services/aiService'
import './AIToolbar.css'

export const AIToolbar: React.FC = () => {
  const { nodes, edges, aiEnabled, toggleAI, addNode, addEdge } = useCanvasStore()
  const [loading, setLoading] = useState(false)
  const [userIntent, setUserIntent] = useState('')

  const handleAISuggest = async () => {
    if (!userIntent.trim()) return

    setLoading(true)
    try {
      const suggestions = await aiService.generateNodeSuggestions({
        nodes,
        edges,
        userIntent,
      })

      // 应用建议
      suggestions.forEach((suggestion) => {
        if (suggestion.type === 'node' && suggestion.data) {
          const nodeData = suggestion.data as any
          const newNode = {
            id: `node-${Date.now()}-${Math.random()}`,
            type: nodeData.type || 'custom',
            position: nodeData.position || { x: 0, y: 0 },
            data: {
              label: nodeData.data?.label || '新节点',
              ...nodeData.data,
              aiGenerated: true,
              aiSuggestion: suggestion.suggestion,
            },
          }
          addNode(newNode as any)
        } else if (suggestion.type === 'edge' && suggestion.data) {
          const edgeData = suggestion.data as any
          const newEdge = {
            id: `edge-${Date.now()}`,
            source: edgeData.source || '',
            target: edgeData.target || '',
            sourceHandle: edgeData.sourceHandle,
            targetHandle: edgeData.targetHandle,
            aiGenerated: true,
          }
          addEdge(newEdge as any)
        }
      })

      setUserIntent('')
    } catch (error) {
      console.error('AI suggestion failed:', error)
      alert('AI建议生成失败，请检查API配置')
    } finally {
      setLoading(false)
    }
  }

  const handleAutoLayout = async () => {
    setLoading(true)
    try {
      const optimizedNodes = await aiService.autoLayout(nodes, edges)
      optimizedNodes.forEach((node) => {
        useCanvasStore.getState().updateNode(node.id, { position: node.position })
      })
    } catch (error) {
      console.error('Auto layout failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSmartConnect = async () => {
    if (nodes.length < 2) return

    setLoading(true)
    try {
      const sourceNode = nodes[0]
      const suggestions = await aiService.suggestConnections(nodes, sourceNode.id)

      suggestions.forEach((suggestion) => {
        if (suggestion.type === 'edge' && suggestion.data) {
          const newEdge = {
            id: `edge-${Date.now()}-${Math.random()}`,
            ...suggestion.data,
            aiGenerated: true,
          }
          addEdge(newEdge as any)
        }
      })
    } catch (error) {
      console.error('Smart connect failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ai-toolbar">
      <div className="ai-toolbar-header">
        <label>
          <input
            type="checkbox"
            checked={aiEnabled}
            onChange={toggleAI}
          />
          <span>🤖 AI智能助手</span>
        </label>
      </div>

      {aiEnabled && (
        <div className="ai-toolbar-content">
          <div className="ai-input-group">
            <input
              type="text"
              placeholder="描述你的需求..."
              value={userIntent}
              onChange={(e) => setUserIntent(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAISuggest()}
              disabled={loading}
            />
            <button onClick={handleAISuggest} disabled={loading}>
              {loading ? '生成中...' : '智能推荐'}
            </button>
          </div>

          <div className="ai-actions">
            <button onClick={handleAutoLayout} disabled={loading}>
              🤖 智能布局
            </button>
            <button onClick={handleSmartConnect} disabled={loading}>
              🔗 智能连线
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
