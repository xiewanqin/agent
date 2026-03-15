import React, { useCallback, useEffect, useRef } from 'react'
import ReactFlow, {
  Node as ReactFlowNode,
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeTypes,
  Panel,
} from 'reactflow'
import 'reactflow/dist/style.css'
import './ReactFlowStyles.css'
import { useCanvasStore } from '@/store/canvasStore'
import { CustomNode } from './CustomNode'
import { AIToolbar } from '../AIToolbar/AIToolbar'
import { PerformanceMonitor } from '../PerformanceMonitor/PerformanceMonitor'
import { aiService } from '@/services/aiService'

const nodeTypes: NodeTypes = {
  custom: CustomNode,
  input: CustomNode,
  output: CustomNode,
  process: CustomNode,
  decision: CustomNode,
  agent: CustomNode,
  rag: CustomNode,
  llm: CustomNode,
}

export const IntelligentCanvas: React.FC = () => {
  console.log('IntelligentCanvas 组件开始渲染')
  
  const {
    nodes: storeNodes,
    edges: storeEdges,
    aiEnabled,
    addNode,
    addEdge: addEdgeToStore,
    selectNode,
    updateViewport,
  } = useCanvasStore()

  console.log('Store 状态:', { nodesCount: storeNodes.length, edgesCount: storeEdges.length })

  const [nodes, setNodes, onNodesChange] = useNodesState(storeNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(storeEdges)
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [reactFlowInstance, setReactFlowInstance] = React.useState<any>(null)
  
  console.log('ReactFlow 状态:', { nodesCount: nodes.length, edgesCount: edges.length })

  // 同步store状态到ReactFlow
  useEffect(() => {
    setNodes(storeNodes)
    setEdges(storeEdges)
  }, [storeNodes, storeEdges, setNodes, setEdges])

  // 初始化AI服务
  useEffect(() => {
    const apiKey = import.meta.env.VITE_OPENAI_API_KEY
    const baseURL = import.meta.env.VITE_OPENAI_BASE_URL || 'https://api.openai.com/v1'
    const model = import.meta.env.VITE_MODEL_NAME || 'gpt-4'

    if (apiKey) {
      aiService.initialize({
        apiKey,
        baseURL,
        model,
        temperature: 0.7,
        maxTokens: 1000,
      })
    }
  }, [])

  const onConnect = useCallback(
    (params: Connection) => {
      if (!params.source || !params.target) return
      
      const newEdge = {
        ...params,
        id: `edge-${params.source}-${params.target}`,
        animated: aiEnabled,
      }
      setEdges((eds) => addEdge(newEdge, eds))
      addEdgeToStore({
        id: newEdge.id,
        source: params.source,
        target: params.target,
        sourceHandle: (params.sourceHandle ?? undefined) as string | undefined,
        targetHandle: (params.targetHandle ?? undefined) as string | undefined,
        animated: newEdge.animated,
        aiGenerated: false,
      })
    },
    [setEdges, addEdgeToStore, aiEnabled]
  )

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()

      const type = event.dataTransfer.getData('application/reactflow')
      if (!type || !reactFlowInstance) return

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      })

      const newNode: ReactFlowNode = {
        id: `node-${Date.now()}`,
        type: type as any,
        position,
        data: {
          label: `${type} node`,
          aiGenerated: false,
        } as any,
      }

      setNodes((nds) => [...nds, newNode])
      addNode({
        id: newNode.id,
        type: (newNode.type || 'custom') as any,
        position: newNode.position,
        data: newNode.data as any,
      })
    },
    [reactFlowInstance, setNodes, addNode]
  )

  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: ReactFlowNode) => {
      selectNode(node.id)
    },
    [selectNode]
  )

  const onPaneClick = useCallback(() => {
    // 点击空白处清除选择
  }, [])

  const onMove = useCallback(
    (_: any, viewport: any) => {
      updateViewport(viewport)
    },
    [updateViewport]
  )

  console.log('准备渲染 ReactFlow')
  
  return (
    <div 
      className="intelligent-canvas" 
      style={{ 
        width: '100%', 
        height: '100%',
        position: 'relative',
        background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
      }}
    >
      <div ref={reactFlowWrapper} style={{ width: '100%', height: '100%' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          onMove={onMove}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-left"
        >
          <Controls />
          <Background 
            variant={'dots' as any} 
            gap={20} 
            size={1.5}
            color="#667eea33"
            style={{ opacity: 0.3 }}
          />
          <MiniMap />
          <Panel position="top-left">
            <AIToolbar />
          </Panel>
          <Panel position="top-right">
            <PerformanceMonitor />
          </Panel>
        </ReactFlow>
      </div>
    </div>
  )
}
