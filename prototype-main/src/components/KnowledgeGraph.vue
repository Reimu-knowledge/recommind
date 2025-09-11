<template>
  <div class="knowledge-graph-mini">
    <div class="mini-graph-container">
      <svg :width="width" :height="height" class="mini-graph-svg">
        <g>
          <!-- 绘制连线 -->
          <line
            v-for="link in miniGraphData.links"
            :key="`${link.source}-${link.target}`"
            :x1="getNodePosition(link.source).x"
            :y1="getNodePosition(link.source).y"
            :x2="getNodePosition(link.target).x"
            :y2="getNodePosition(link.target).y"
            stroke="#999"
            stroke-opacity="0.6"
            stroke-width="1"
          />
          
          <!-- 绘制节点 -->
          <circle
            v-for="node in miniGraphData.nodes"
            :key="node.id"
            :cx="getNodePosition(node.id).x"
            :cy="getNodePosition(node.id).y"
            :r="node.isCenter ? 12 : 8"
            :fill="node.color"
            :stroke="node.isCenter ? '#fff' : 'none'"
            :stroke-width="node.isCenter ? 2 : 0"
            class="mini-node"
            :class="{ 'center-node': node.isCenter }"
          />
          
          <!-- 绘制节点标签 -->
          <text
            v-for="node in miniGraphData.nodes"
            :key="`label-${node.id}`"
            :x="getNodePosition(node.id).x"
            :y="getNodePosition(node.id).y + 2"
            text-anchor="middle"
            font-size="10px"
            fill="white"
            font-weight="bold"
            class="mini-label"
          >
            {{ truncateLabel(node.name, 4) }}
          </text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { 
  loadKnowledgeGraphData, 
  buildCenteredSubgraph,
  type KnowledgeNode,
  type KnowledgeLink,
  type GraphData
} from '../utils/knowledgeGraphLoader';

// 组件尺寸
const width = 280;
const height = 160;

// 响应式数据
const allNodes = ref<Map<string, KnowledgeNode>>(new Map());
const allLinks = ref<KnowledgeLink[]>([]);
const miniGraphData = ref<GraphData>({ nodes: [], links: [] });

onMounted(async () => {
  await initializeData();
  // 默认以根节点"4图论"作为中心
  setCenter('k0');
});

// 初始化数据
const initializeData = async () => {
  try {
    const { nodes, links } = await loadKnowledgeGraphData();
    allNodes.value = nodes;
    allLinks.value = links;
  } catch (error) {
    console.error('初始化知识图谱数据失败:', error);
  }
};

// 设置中心节点并更新图形
const setCenter = (centerId: string) => {
  const centerNode = allNodes.value.get(centerId);
  if (!centerNode) return;

  // 使用工具函数构建以该节点为中心的子图
  const subgraph = buildCenteredSubgraph(centerId, allNodes.value, allLinks.value);
  
  miniGraphData.value = subgraph;
};

// 获取节点位置（简单的圆形布局）
const getNodePosition = (nodeId: string) => {
  const nodeIndex = miniGraphData.value.nodes.findIndex(n => n.id === nodeId);
  if (nodeIndex === -1) return { x: 0, y: 0 };
  
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2.5;
  
  if (nodeIndex === 0) {
    // 中心节点
    return { x: centerX, y: centerY };
  } else {
    // 周围节点
    const angle = (2 * Math.PI * (nodeIndex - 1)) / (miniGraphData.value.nodes.length - 1);
    return {
      x: centerX + radius * Math.cos(angle),
      y: centerY + radius * Math.sin(angle)
    };
  }
};

// 截断标签
const truncateLabel = (name: string, limit: number = 3): string => {
  if (!name) return '';
  return name.length > limit ? name.slice(0, limit) + '...' : name;
};
</script>

<style scoped>
.knowledge-graph-mini {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.mini-graph-container {
  width: 280px;
  height: 160px;
  background: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.mini-graph-svg {
  width: 100%;
  height: 100%;
}

.mini-node {
  cursor: pointer;
  transition: all 0.2s ease;
}

.mini-node:hover {
  stroke-width: 2px !important;
  filter: brightness(1.2);
}

.center-node {
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
}

.mini-label {
  pointer-events: none;
  user-select: none;
}
</style>