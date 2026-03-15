import React, { useEffect, useState } from 'react'
import { useCanvasStore } from '@/store/canvasStore'
import './PerformanceMonitor.css'

export const PerformanceMonitor: React.FC = () => {
  const { performanceMode, setPerformanceMode, nodes, edges } = useCanvasStore()
  const [fps, setFps] = useState(60)
  const [renderTime, setRenderTime] = useState(0)

  useEffect(() => {
    let frameCount = 0
    let lastTime = performance.now()
    let animationFrame: number

    const measureFPS = () => {
      frameCount++
      const currentTime = performance.now()
      const delta = currentTime - lastTime

      if (delta >= 1000) {
        setFps(frameCount)
        frameCount = 0
        lastTime = currentTime
      }

      animationFrame = requestAnimationFrame(measureFPS)
    }

    animationFrame = requestAnimationFrame(measureFPS)

    return () => {
      cancelAnimationFrame(animationFrame)
    }
  }, [])

  useEffect(() => {
    const startTime = performance.now()
    // 模拟渲染时间测量
    requestAnimationFrame(() => {
      const endTime = performance.now()
      setRenderTime(endTime - startTime)
    })
  }, [nodes, edges])

  const nodeCount = nodes.length
  const edgeCount = edges.length
  const totalElements = nodeCount + edgeCount

  const getPerformanceStatus = () => {
    if (fps >= 55) return { status: 'excellent', color: '#4caf50' }
    if (fps >= 30) return { status: 'good', color: '#ff9800' }
    return { status: 'poor', color: '#f44336' }
  }

  const perfStatus = getPerformanceStatus()

  return (
    <div className="performance-monitor">
      <div className="performance-header">
        <span>⚡ 性能监控</span>
        <select
          value={performanceMode}
          onChange={(e) =>
            setPerformanceMode(e.target.value as 'normal' | 'high-performance')
          }
        >
          <option value="normal">普通模式</option>
          <option value="high-performance">高性能模式</option>
        </select>
      </div>

      <div className="performance-stats">
        <div className="stat-item">
          <span className="stat-label">FPS:</span>
          <span className="stat-value" style={{ color: perfStatus.color }}>
            {fps}
          </span>
        </div>
        <div className="stat-item">
          <span className="stat-label">渲染时间:</span>
          <span className="stat-value">{renderTime.toFixed(2)}ms</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">节点数:</span>
          <span className="stat-value">{nodeCount}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">连接数:</span>
          <span className="stat-value">{edgeCount}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">总元素:</span>
          <span className="stat-value">{totalElements}</span>
        </div>
      </div>

      {performanceMode === 'high-performance' && (
        <div className="performance-warning">
          ⚡ 高性能模式已启用（使用Web Workers和虚拟滚动）
        </div>
      )}
    </div>
  )
}
