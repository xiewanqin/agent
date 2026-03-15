import { create } from 'zustand'
import { Node, Edge, CanvasState, AISuggestion } from '@/types'

interface CanvasStore extends CanvasState {
  // Actions
  addNode: (node: Node) => void
  updateNode: (id: string, updates: Partial<Node>) => void
  deleteNode: (id: string) => void
  addEdge: (edge: Edge) => void
  deleteEdge: (id: string) => void
  selectNode: (id: string, multi?: boolean) => void
  selectEdge: (id: string, multi?: boolean) => void
  clearSelection: () => void
  updateViewport: (viewport: Partial<CanvasState['viewport']>) => void
  setAISuggestions: (suggestions: AISuggestion[]) => void
  toggleAI: () => void
  setPerformanceMode: (mode: 'normal' | 'high-performance') => void
  // 批量操作
  importCanvas: (nodes: Node[], edges: Edge[]) => void
  exportCanvas: () => { nodes: Node[]; edges: Edge[] }
}

const initialState: CanvasState = {
  nodes: [],
  edges: [],
  selectedNodes: [],
  selectedEdges: [],
  viewport: {
    x: 0,
    y: 0,
    zoom: 1,
  },
  aiEnabled: true,
  performanceMode: 'normal',
}

export const useCanvasStore = create<CanvasStore>((set, get) => ({
  ...initialState,

  addNode: (node) =>
    set((state) => ({
      nodes: [...state.nodes, node],
    })),

  updateNode: (id, updates) =>
    set((state) => ({
      nodes: state.nodes.map((node) =>
        node.id === id ? { ...node, ...updates } : node
      ),
    })),

  deleteNode: (id) =>
    set((state) => ({
      nodes: state.nodes.filter((node) => node.id !== id),
      edges: state.edges.filter(
        (edge) => edge.source !== id && edge.target !== id
      ),
      selectedNodes: state.selectedNodes.filter((nodeId) => nodeId !== id),
    })),

  addEdge: (edge) =>
    set((state) => ({
      edges: [...state.edges, edge],
    })),

  deleteEdge: (id) =>
    set((state) => ({
      edges: state.edges.filter((edge) => edge.id !== id),
      selectedEdges: state.selectedEdges.filter((edgeId) => edgeId !== id),
    })),

  selectNode: (id, multi = false) =>
    set((state) => ({
      selectedNodes: multi
        ? state.selectedNodes.includes(id)
          ? state.selectedNodes.filter((n) => n !== id)
          : [...state.selectedNodes, id]
        : [id],
      selectedEdges: [],
    })),

  selectEdge: (id, multi = false) =>
    set((state) => ({
      selectedEdges: multi
        ? state.selectedEdges.includes(id)
          ? state.selectedEdges.filter((e) => e !== id)
          : [...state.selectedEdges, id]
        : [id],
      selectedNodes: [],
    })),

  clearSelection: () =>
    set({
      selectedNodes: [],
      selectedEdges: [],
    }),

  updateViewport: (viewport) =>
    set((state) => ({
      viewport: { ...state.viewport, ...viewport },
    })),

  setAISuggestions: (suggestions) => {
    // AI建议处理逻辑
    console.log('AI Suggestions:', suggestions)
  },

  toggleAI: () =>
    set((state) => ({
      aiEnabled: !state.aiEnabled,
    })),

  setPerformanceMode: (mode) =>
    set({
      performanceMode: mode,
    }),

  importCanvas: (nodes, edges) =>
    set({
      nodes,
      edges,
    }),

  exportCanvas: () => {
    const state = get()
    return {
      nodes: state.nodes,
      edges: state.edges,
    }
  },
}))
