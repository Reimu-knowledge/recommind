<template>
  <div class="interactive-knowledge-graph">
    <div class="graph-header">
      <h3>交互式知识图谱</h3>
      <div class="current-center">
        当前中心: {{ currentCenter?.name || '加载中...' }}
      </div>
      <button class="reset-btn" @click="resetGraph">重置</button>
    </div>
    <div id="interactive-graph" class="graph-content"></div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, reactive } from 'vue';
import * as d3 from 'd3';
import { 
  loadKnowledgeGraphData, 
  buildCenteredSubgraph,
  type KnowledgeNode,
  type KnowledgeLink,
  type GraphData
} from '../utils/knowledgeGraphLoader';

// 响应式数据
const currentCenter = ref<KnowledgeNode | null>(null);
const allNodes = ref<Map<string, KnowledgeNode>>(new Map());
const allLinks = ref<KnowledgeLink[]>([]);
const currentGraphData = reactive<GraphData>({ nodes: [], links: [] });

let chartInstance: any = null;
let simulation: any = null;

onMounted(async () => {
  await initializeData();
  // 默认以根节点"4图论"作为中心
  setCenter('k0');
});

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.remove();
  }
});

// 重置到初始中心节点
const resetGraph = () => {
  setCenter('k0');
};

// 初始化数据
const initializeData = async () => {
  try {
    const { nodes, links } = await loadKnowledgeGraphData();
    allNodes.value = nodes;
    allLinks.value = links;
    console.log(`加载了 ${nodes.size} 个节点和 ${links.length} 条连接`);
  } catch (error) {
    console.error('初始化知识图谱数据失败:', error);
  }
};

// 设置中心节点并更新图形
const setCenter = (centerId: string) => {
  const centerNode = allNodes.value.get(centerId);
  if (!centerNode) return;

  currentCenter.value = centerNode;

  // 使用工具函数构建以该节点为中心的子图
  const subgraph = buildCenteredSubgraph(centerId, allNodes.value, allLinks.value);
  
  currentGraphData.nodes = subgraph.nodes;
  currentGraphData.links = subgraph.links;

  // 重新渲染图形
  renderGraph();
};

// 渲染图形
const renderGraph = () => {
  // 清除之前的图形
  d3.select('#interactive-graph').selectAll('*').remove();

  const container = d3.select('#interactive-graph');
  const width = 1200;  // 增加画布宽度
  const height = 800;   // 增加画布高度
  
  const svg = container
    .append('svg')
    .attr('width', width)
    .attr('height', height)
    .attr('viewBox', [0, 0, width, height]);

  chartInstance = svg;

  // 创建力导向图（为兼容TS类型，进行显式any断言）
  simulation = d3.forceSimulation<any>(currentGraphData.nodes as any)
    .force('link', d3.forceLink<any, any>(currentGraphData.links as any).id((d: any) => d.id).distance(250))  // 进一步增加节点间距
    .force('charge', d3.forceManyBody().strength(-800))  // 增加排斥力
    .force('collide', d3.forceCollide().radius((d: any) => d.isCenter ? 120 : 80).strength(1))  // 增加碰撞检测半径
    .force('center', d3.forceCenter(width / 2, height / 2));

  // 绘制连线 - 加粗并增加箭头
  const defs = svg.append('defs');
  
  // 添加箭头标记
  defs.append('marker')
    .attr('id', 'arrowhead')
    .attr('viewBox', '0 0 10 10')
    .attr('refX', 8)
    .attr('refY', 5)
    .attr('markerWidth', 6)
    .attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path')
    .attr('d', 'M 0 0 L 10 5 L 0 10 z')
    .attr('fill', '#999');

  const link = svg.append('g')
    .selectAll('line')
    .data(currentGraphData.links)
    .join('line')
    .attr('stroke', '#555')
    .attr('stroke-opacity', 0.9)
    .attr('stroke-width', 4)  // 加粗连线
    .attr('stroke-linecap', 'round')  // 更平滑的线端
    .attr('marker-end', 'url(#arrowhead)');

  // 绘制节点组
  const node: any = svg.append('g')
    .selectAll('g')
    .data(currentGraphData.nodes)
    .join('g')
    .style('cursor', 'pointer')
    .call((d3.drag() as any)
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended))
    .on('click', (event, d: any) => {
      if (!d.isCenter) {
        setCenter(d.id);
      }
    });

  // 节点圆圈 - 进一步放大节点
  node.append('circle')
    .attr('r', (d: any) => d.isCenter ? 100 : 70)  // 中心节点100px，邻居节点70px
    .attr('fill', (d: any) => d.color)
    .attr('stroke', '#fff')
    .attr('stroke-width', (d: any) => d.isCenter ? 10 : 7)  // 加粗描边
    .style('filter', (d: any) => d.isCenter ? 'drop-shadow(0 8px 16px rgba(0,0,0,0.3))' : 'drop-shadow(0 5px 10px rgba(0,0,0,0.2))');

  // 节点文字 - 显示完整文本并调整样式
  node.append('text')
    .text((d: any) => d.name)  // 显示完整文本
    .attr('text-anchor', 'middle')
    .attr('dy', '0.35em')
    .attr('font-size', (d: any) => d.isCenter ? '32px' : '24px')  // 进一步增大字体
    .attr('font-weight', (d: any) => d.isCenter ? 'bold' : 'normal')
    .attr('fill', 'white')
    .style('pointer-events', 'none')
    .style('text-shadow', '2px 2px 4px rgba(0,0,0,0.6)')  // 增强文字阴影
    .style('user-select', 'none')  // 防止文字被选中
    .style('font-family', '"Microsoft YaHei", sans-serif');  // 使用更清晰的字体

  // 添加节点标题提示
  node.append('title')
    .text((d: any) => d.name);

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

// 截断标签至指定长度，超过则加省略号
const truncateLabel = (name: string, limit: number = 6): string => {
  if (!name) return '';
  return name.length > limit ? name.slice(0, limit) + '...' : name;
};
</script>

<style scoped>
.interactive-knowledge-graph {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
}

.graph-header {
  padding: 20px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  position: relative;
}

.graph-header h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  font-weight: bold;
}

.current-center {
  font-size: 14px;
  opacity: 0.9;
  background: rgba(255, 255, 255, 0.2);
  padding: 5px 15px;
  border-radius: 15px;
  display: inline-block;
}

.reset-btn {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  background: #ffffff;
  color: #4f46e5;
  border: none;
  padding: 6px 12px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}

.reset-btn:hover {
  filter: brightness(0.95);
}

.graph-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f2f5;
  padding: 20px;
  overflow: auto;
}

/* 滚动条样式 */
.graph-content::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.graph-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.graph-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.graph-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

#interactive-graph svg {
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 节点悬停效果 */
:deep(.node-group:hover circle) {
  stroke-width: 3px;
  filter: brightness(1.1);
}
</style>
