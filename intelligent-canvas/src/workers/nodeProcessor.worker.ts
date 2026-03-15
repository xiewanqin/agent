// Web Worker for node processing
self.onmessage = function (e: MessageEvent) {
  const { nodes, operation } = e.data

  let result: any

  switch (operation) {
    case 'layout':
      result = calculateLayout(nodes)
      break
    case 'collision':
      result = detectCollisions(nodes)
      break
    default:
      result = nodes
  }

  self.postMessage({ operation, result })
}

function calculateLayout(nodes: any[]): any[] {
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

        fx += (repulsion / distance) * (dx / distance)
        fy += (repulsion / distance) * (dy / distance)
      })

      node.position.x += fx * 0.1
      node.position.y += fy * 0.1
    })
  }

  return nodes
}

function detectCollisions(nodes: any[]): any[] {
  return nodes.map((node) => {
    const collisions = nodes.filter((other) => {
      if (other.id === node.id) return false
      const dx = node.position.x - other.position.x
      const dy = node.position.y - other.position.y
      const distance = Math.sqrt(dx * dx + dy * dy)
      return distance < 100
    })
    return { ...node, collisions: collisions.length }
  })
}
