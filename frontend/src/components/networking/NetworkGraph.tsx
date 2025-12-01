import React, { useEffect, useRef, useState } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

interface ApiGraphData {
  nodes: any[];
  edges: any[];
}

interface GraphData {
  nodes: any[];
  links: any[];
}

interface NetworkGraphProps {
  data?: ApiGraphData;
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({ data }) => {
  const fgRef = useRef<any>();
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // If data is provided (from chatbot), use it
    if (data && data.nodes.length > 0) {
      // Map edges to links for react-force-graph
      setGraphData({
        nodes: [...data.nodes],
        links: data.edges.map((e: any) => ({ source: e.source, target: e.target }))
      });
    } else {
      // Otherwise fetch full graph
      fetch('http://localhost:8000/api/v1/networking/graph')
        .then(res => res.json())
        .then(data => {
            setGraphData({
                nodes: data.nodes,
                links: data.edges.map((e: any) => ({ source: e.source, target: e.target }))
            });
        })
        .catch(err => console.error("Failed to fetch graph", err));
    }
  }, [data]);

  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        setDimensions({
          width: containerRef.current.offsetWidth,
          height: containerRef.current.offsetHeight
        });
      }
    };

    window.addEventListener('resize', updateDimensions);
    updateDimensions();

    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  return (
    <div ref={containerRef} style={{ width: '100%', height: '100%', minHeight: '500px', border: '1px solid var(--color-border)', borderRadius: 'var(--radius-lg)', overflow: 'hidden' }}>
      <ForceGraph2D
        ref={fgRef}
        width={dimensions.width}
        height={dimensions.height}
        graphData={graphData}
        nodeLabel="label"
        nodeAutoColorBy="group"
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={() => 0.005}
        backgroundColor="#ffffff"
        nodeCanvasObject={(node: any, ctx, globalScale) => {
          const label = node.label;
          const fontSize = 12/globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          const textWidth = ctx.measureText(label).width;
          const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2); // some padding

          ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
          if (node.group === 1) ctx.fillStyle = '#e6f7ff'; // Student
          if (node.group === 2) ctx.fillStyle = '#fff7e6'; // Faculty
          if (node.group === 3) ctx.fillStyle = '#f6ffed'; // Skill
          
          ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);

          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = node.color || '#000';
          if (node.group === 1) ctx.fillStyle = '#0066cc';
          if (node.group === 2) ctx.fillStyle = '#d35400';
          if (node.group === 3) ctx.fillStyle = '#27ae60';
          
          ctx.fillText(label, node.x, node.y);

          node.__bckgDimensions = bckgDimensions; // to re-use in nodePointerAreaPaint
        }}
        nodePointerAreaPaint={(node: any, color, ctx) => {
          ctx.fillStyle = color;
          const bckgDimensions = node.__bckgDimensions;
          bckgDimensions && ctx.fillRect(node.x - bckgDimensions[0] / 2, node.y - bckgDimensions[1] / 2, bckgDimensions[0], bckgDimensions[1]);
        }}
      />
    </div>
  );
};

export default NetworkGraph;
