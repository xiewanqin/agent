import React, { memo } from 'react'
import { Handle, Position, NodeProps } from 'reactflow'
import { NodeData } from '@/types'
import './CustomNode.css'

interface CustomNodeData extends NodeData {
  label: string
  description?: string
  aiGenerated?: boolean
  aiSuggestion?: string
}

const nodeStyles: Record<string, { bg: string; border: string; gradient: string }> = {
  input: {
    bg: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    border: '#667eea',
    gradient: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
  },
  output: {
    bg: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    border: '#f5576c',
    gradient: 'linear-gradient(135deg, rgba(240, 147, 251, 0.1) 0%, rgba(245, 87, 108, 0.1) 100%)',
  },
  process: {
    bg: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    border: '#4facfe',
    gradient: 'linear-gradient(135deg, rgba(79, 172, 254, 0.1) 0%, rgba(0, 242, 254, 0.1) 100%)',
  },
  decision: {
    bg: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    border: '#fa709a',
    gradient: 'linear-gradient(135deg, rgba(250, 112, 154, 0.1) 0%, rgba(254, 225, 64, 0.1) 100%)',
  },
  agent: {
    bg: 'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
    border: '#30cfd0',
    gradient: 'linear-gradient(135deg, rgba(48, 207, 208, 0.1) 0%, rgba(51, 8, 103, 0.1) 100%)',
  },
  rag: {
    bg: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    border: '#a8edea',
    gradient: 'linear-gradient(135deg, rgba(168, 237, 234, 0.1) 0%, rgba(254, 214, 227, 0.1) 100%)',
  },
  llm: {
    bg: 'linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)',
    border: '#fcb69f',
    gradient: 'linear-gradient(135deg, rgba(255, 236, 210, 0.1) 0%, rgba(252, 182, 159, 0.1) 100%)',
  },
  custom: {
    bg: 'linear-gradient(135deg, #ffffff 0%, #f5f7fa 100%)',
    border: '#d1d5db',
    gradient: 'linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(245, 247, 250, 0.1) 100%)',
  },
}

export const CustomNode = memo(({ data, selected, type = 'custom' }: NodeProps<{ data: CustomNodeData }>) => {
  const nodeType = (type || 'custom') as string
  const style = nodeStyles[nodeType] || nodeStyles.custom
  const nodeData = (data as unknown) as CustomNodeData

  return (
    <div
      className="custom-node-wrapper"
      style={{
        background: 'white',
        padding: '14px 16px',
        borderRadius: '12px',
        borderWidth: selected ? '3px' : '2px',
        borderStyle: 'solid',
        borderColor: selected ? style.border : 'rgba(0, 0, 0, 0.1)',
        minWidth: '140px',
        boxShadow: selected 
          ? `0 8px 24px rgba(0, 0, 0, 0.15), 0 0 0 4px ${style.border}33` 
          : '0 4px 12px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* 渐变装饰条 */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: style.bg,
          opacity: selected ? 1 : 0.6,
        }}
      />
      
      <Handle 
        type="target" 
        position={Position.Top}
        style={{
          width: '12px',
          height: '12px',
          background: style.border,
          border: '2px solid white',
        }}
      />
      
      <div style={{ 
        fontWeight: '600', 
        fontSize: '14px',
        marginBottom: nodeData.description ? '6px' : '0',
        color: '#1a1a1a',
        lineHeight: '1.4',
      }}>
        {nodeData.label}
      </div>
      
      {nodeData.description && (
        <div style={{ 
          fontSize: '12px', 
          color: '#666', 
          marginBottom: '8px',
          lineHeight: '1.4',
        }}>
          {nodeData.description}
        </div>
      )}
      
      {nodeData.aiGenerated && (
        <div
          style={{
            fontSize: '10px',
            color: '#9c27b0',
            fontStyle: 'italic',
            marginTop: '8px',
            padding: '4px 8px',
            background: 'linear-gradient(135deg, rgba(156, 39, 176, 0.1) 0%, rgba(233, 30, 99, 0.1) 100%)',
            borderRadius: '6px',
            display: 'inline-block',
            fontWeight: '500',
          }}
        >
          ✨ AI生成
        </div>
      )}
      
      {nodeData.aiSuggestion && (
        <div
          style={{
            fontSize: '11px',
            color: '#ff6b35',
            marginTop: '8px',
            padding: '6px 10px',
            background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.1) 0%, rgba(255, 107, 53, 0.1) 100%)',
            borderRadius: '6px',
            border: '1px solid rgba(255, 152, 0, 0.2)',
          }}
        >
          💡 {nodeData.aiSuggestion}
        </div>
      )}
      
      <Handle 
        type="source" 
        position={Position.Bottom}
        style={{
          width: '12px',
          height: '12px',
          background: style.border,
          border: '2px solid white',
        }}
      />
    </div>
  )
})

CustomNode.displayName = 'CustomNode'
