<template>
  <div class="knowledge-graph-container">
    <div id="knowledge-graph" class="graph-content"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import * as d3 from 'd3';

// 模拟知识图谱数据
const graphData = {
  nodes: [
    { id: 'discrete', name: '离散数学', level: 0, color: '#FF6B6B', isCenter: true },
    { id: 'sets', name: '集合论', level: 1, color: '#409EFF' },
    { id: 'logic', name: '数理逻辑', level: 1, color: '#67C23A' },
    { id: 'graph', name: '图论', level: 1, color: '#E6A23C' },
    { id: 'algebra', name: '代数系统', level: 1, color: '#8E44AD' }
  ],
  links: [
    { source: 'discrete', target: 'sets' },
    { source: 'discrete', target: 'logic' },
    { source: 'discrete', target: 'graph' },
    { source: 'discrete', target: 'algebra' }
  ]
};

onMounted(() => {
  initGraph();
});

const initGraph = () => {
  const container = d3.select('#knowledge-graph');
  const width = 600;
  const height = 400;
  
  const svg = container
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height]);

  // 创建力导向图
  const simulation = d3.forceSimulation(graphData.nodes)
    .force('link', d3.forceLink(graphData.links).id((d: any) => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-300))
    .force('center', d3.forceCenter(width / 2, height / 2));

  // 绘制连线
  const link = svg.append('g')
    .selectAll('line')
    .data(graphData.links)
    .join('line')
    .attr('stroke', '#999')
    .attr('stroke-opacity', 0.6)
    .attr('stroke-width', 2);

  // 绘制节点
  const node = svg.append('g')
    .selectAll('g')
    .data(graphData.nodes)
    .join('g')
    .call(d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended));

  // 节点圆圈
  node.append('circle')
    .attr('r', (d: any) => d.isCenter ? 35 : 25)
    .attr('fill', (d: any) => d.color)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .style('cursor', 'pointer');

  // 节点文字
  node.append('text')
    .text((d: any) => d.name)
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('font-size', '12px')
    .attr('fill', 'white')
    .style('pointer-events', 'none');

  simulation.on('tick', () => {
    link
      .attr('x1', (d: any) => d.source.x)
      .attr('y1', (d: any) => d.source.y)
      .attr('x2', (d: any) => d.target.x)
      .attr('y2', (d: any) => d.target.y);

    node
      .attr('transform', (d: any) => `translate(${d.x},${d.y})`);
  });

  function dragstarted(event: any) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }

  function dragged(event: any) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }

  function dragended(event: any) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
};
</script>

<style scoped>
.knowledge-graph-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.graph-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #fff;
}

#knowledge-graph svg {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
