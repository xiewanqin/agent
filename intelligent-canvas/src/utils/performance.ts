// Web Workers 性能优化工具

// 在Web Worker中处理大量节点计算
export class NodeProcessor {
  private worker: Worker | null = null

  constructor() {
    if (typeof Worker !== 'undefined') {
      this.worker = new Worker(
        new URL('../workers/nodeProcessor.worker.ts', import.meta.url),
        { type: 'module' }
      )
    }
  }

  async processNodes(nodes: any[], operation: string): Promise<any> {
    if (!this.worker) {
      // Fallback to main thread
      return this.processInMainThread(nodes, operation)
    }

    return new Promise((resolve, reject) => {
      const handler = (e: MessageEvent) => {
        if (e.data.operation === operation) {
          if (this.worker) {
            this.worker.removeEventListener('message', handler)
          }
          resolve(e.data.result)
        }
      }

      if (this.worker) {
        this.worker.addEventListener('message', handler)
        this.worker.addEventListener('error', reject)
        this.worker.postMessage({ nodes, operation })
      }
    })
  }

  private processInMainThread(nodes: any[], operation: string): any {
    // 主线程处理逻辑
    switch (operation) {
      case 'layout':
        return this.calculateLayout(nodes)
      case 'collision':
        return this.detectCollisions(nodes)
      default:
        return nodes
    }
  }

  private calculateLayout(nodes: any[]): any[] {
    // 简单的力导向布局计算
    const iterations = 50
    const k = Math.sqrt((1000 * 1000) / nodes.length)
    const repulsion = k * k

    for (let i = 0; i < iterations; i++) {
      nodes.forEach((node, idx) => {
        let fx = 0
        let fy = 0

        nodes.forEach((other, otherIdx) => {
          if (idx === otherIdx) return

          const dx = node.position.x - other.position.x
          const dy = node.position.y - other.position.y
          const distance = Math.sqrt(dx * dx + dy * dy) || 1

          // 排斥力
          fx += (repulsion / distance) * (dx / distance)
          fy += (repulsion / distance) * (dy / distance)
        })

        node.position.x += fx * 0.1
        node.position.y += fy * 0.1
      })
    }

    return nodes
  }

  private detectCollisions(nodes: any[]): any[] {
    // 碰撞检测
    return nodes.map((node) => {
      const collisions = nodes.filter((other) => {
        if (other.id === node.id) return false
        const dx = node.position.x - other.position.x
        const dy = node.position.y - other.position.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        return distance < 100 // 假设节点最小间距为100
      })
      return { ...node, collisions: collisions.length }
    })
  }

  destroy() {
    this.worker?.terminate()
  }
}

// Canvas渲染性能优化
export class CanvasOptimizer {
  private offscreenCanvas: OffscreenCanvas | null = null
  private ctx: OffscreenCanvasRenderingContext2D | null = null

  initialize(width: number, height: number) {
    if (typeof OffscreenCanvas !== 'undefined') {
      this.offscreenCanvas = new OffscreenCanvas(width, height)
      const ctx = this.offscreenCanvas.getContext('2d')
      if (ctx) {
        this.ctx = ctx
      }
    }
  }

  renderNodes(nodes: any[], scale: number = 1): ImageBitmap | null {
    if (!this.ctx || !this.offscreenCanvas) return null

    const width = this.offscreenCanvas.width
    const height = this.offscreenCanvas.height
    if (width && height) {
      this.ctx.clearRect(0, 0, width, height)
    }
    this.ctx.save()
    this.ctx.scale(scale, scale)

    nodes.forEach((node) => {
      this.ctx!.fillStyle = node.style?.backgroundColor || '#fff'
      this.ctx!.strokeStyle = node.style?.borderColor || '#000'
      this.ctx!.lineWidth = node.style?.borderWidth || 1

      const x = node.position.x
      const y = node.position.y
      const w = node.width || 100
      const h = node.height || 50

      this.ctx!.fillRect(x, y, w, h)
      this.ctx!.strokeRect(x, y, w, h)

      // 绘制文本
      this.ctx!.fillStyle = node.style?.color || '#000'
      this.ctx!.font = `${node.style?.fontSize || 14}px Arial`
      this.ctx!.fillText(node.data.label, x + 10, y + 25)
    })

    this.ctx.restore()
    return this.offscreenCanvas.transferToImageBitmap()
  }

  destroy() {
    this.offscreenCanvas = null
    this.ctx = null
  }
}

// 虚拟滚动优化（处理大量节点）
export class VirtualScroller {
  private viewport: { x: number; y: number; width: number; height: number }
  private itemHeight: number
  private itemWidth: number

  constructor(
    viewport: { x: number; y: number; width: number; height: number },
    itemSize: { width: number; height: number }
  ) {
    this.viewport = viewport
    this.itemWidth = itemSize.width
    this.itemHeight = itemSize.height
  }

  getVisibleItems(items: any[]): any[] {
    const startX = Math.floor(this.viewport.x / this.itemWidth)
    const endX = Math.ceil(
      (this.viewport.x + this.viewport.width) / this.itemWidth
    )
    const startY = Math.floor(this.viewport.y / this.itemHeight)
    const endY = Math.ceil(
      (this.viewport.y + this.viewport.height) / this.itemHeight
    )

    return items.filter((_item, index) => {
      const x = Math.floor(index % 10) // 假设每行10个
      const y = Math.floor(index / 10)
      return x >= startX && x <= endX && y >= startY && y <= endY
    })
  }

  updateViewport(viewport: Partial<typeof this.viewport>) {
    this.viewport = { ...this.viewport, ...viewport }
  }
}
