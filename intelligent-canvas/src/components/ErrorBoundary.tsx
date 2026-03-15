import { Component, ErrorInfo, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('错误边界捕获到错误:', error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: '20px',
            margin: '20px',
            border: '1px solid #f44336',
            borderRadius: '4px',
            backgroundColor: '#ffebee',
          }}
        >
          <h2 style={{ color: '#c62828' }}>⚠️ 应用出现错误</h2>
          <p style={{ color: '#d32f2f' }}>
            {this.state.error?.message || '未知错误'}
          </p>
          <details style={{ marginTop: '10px' }}>
            <summary>错误详情</summary>
            <pre style={{ marginTop: '10px', padding: '10px', backgroundColor: '#fff', overflow: 'auto' }}>
              {this.state.error?.stack}
            </pre>
          </details>
          <button
            onClick={() => window.location.reload()}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: '#2196f3',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
            }}
          >
            重新加载页面
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
