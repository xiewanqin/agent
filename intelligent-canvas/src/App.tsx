import { IntelligentCanvas } from './components/Canvas/IntelligentCanvas'
import { NodePalette } from './components/NodePalette/NodePalette'
import './App.css'
import './components/CustomScrollbar.css'

function App() {
  // 添加调试信息
  console.log('App 组件渲染')
  
  return (
    <div className="app">
      <div className="app-sidebar sidebar-scrollbar">
        <NodePalette />
      </div>
      <div className="app-main">
        <IntelligentCanvas />
      </div>
    </div>
  )
}

export default App
