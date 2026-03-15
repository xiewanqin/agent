import React from 'react'
import { NodeType } from '@/types'
import './NodePalette.css'

const nodeTypes: { type: NodeType; label: string; icon: string }[] = [
  { type: 'input', label: '输入', icon: '📥' },
  { type: 'output', label: '输出', icon: '📤' },
  { type: 'process', label: '处理', icon: '⚙️' },
  { type: 'decision', label: '决策', icon: '❓' },
  { type: 'agent', label: 'Agent', icon: '🤖' },
  { type: 'rag', label: 'RAG', icon: '🔍' },
  { type: 'llm', label: 'LLM', icon: '🧠' },
  { type: 'custom', label: '自定义', icon: '📦' },
]

export const NodePalette: React.FC = () => {
  const onDragStart = (event: React.DragEvent, nodeType: NodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType)
    event.dataTransfer.effectAllowed = 'move'
  }

  return (
    <div className="node-palette">
      <div className="node-palette-header">📦 节点类型</div>
      <div className="node-palette-items">
        {nodeTypes.map(({ type, label, icon }) => (
          <div
            key={type}
            className="node-palette-item"
            draggable
            onDragStart={(e) => onDragStart(e, type)}
          >
            <span className="node-icon">{icon}</span>
            <span className="node-label">{label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
