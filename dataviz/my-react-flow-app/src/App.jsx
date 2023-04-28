import 'reactflow/dist/style.css';

import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  Handle,
  MiniMap,
  addEdge,
} from 'reactflow';

const CustomNode = ({ data }) => {
  return (
    <div style={{ padding: '10px', background: 'white', borderRadius: '5px', color: 'black', width: '300px' }}>
      <h3>{data.title}</h3>
      <p>
        {data.content}
      </p>
      <Handle type="source" position="right" id="a" />
      <Handle type="target" position="left" id="b" />
    </div>
  );
};

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);

  useEffect(() => {
    const socket = new WebSocket('ws://localhost:8080'); // Replace this with your server's WebSocket URL.

    socket.onopen = () => {
      console.log('WebSocket connection opened.');
    };

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.nodes) {
        setNodes(data.nodes);
      }

      if (data.edges) {
        setEdges(data.edges);
      }
    };

    socket.onclose = () => {
      console.log('WebSocket connection closed.');
    };

    return () => {
      socket.close();
    };
  }, []);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  // Register the custom node type
  const nodeTypes = {
    custom: CustomNode,
  };

  return (
    <div style={{ width: '100vw', height: '100vh' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onConnect={onConnect}
        nodeTypes={nodeTypes} // Pass the custom node types to ReactFlow
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}
