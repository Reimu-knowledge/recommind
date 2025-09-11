// 知识图谱数据加载器
export interface KnowledgeNode {
  id: string;
  name: string;
  level: number;
  color: string;
  isCenter?: boolean;
}

export interface KnowledgeLink {
  source: string;
  target: string;
  relation: string;
}

export interface GraphData {
  nodes: KnowledgeNode[];
  links: KnowledgeLink[];
}

// 颜色配置
const colors = [
  '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
  '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
  '#F8C471', '#82E0AA', '#AED6F1', '#D7BDE2', '#F9E79F'
];

// 字符串哈希函数
const hashCode = (str: string): number => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return Math.abs(hash);
};

// 获取节点层级（基于ID推断）
const getNodeLevel = (nodeId: string): number => {
  const num = parseInt(nodeId.substring(1));
  if (num === 0) return 0;
  if (num <= 10) return 1;
  if (num <= 50) return 2;
  if (num <= 100) return 3;
  return 4;
};

// 解析CSV数据
export const parseKnowledgeGraphCSV = (csvText: string): { 
  nodes: Map<string, KnowledgeNode>, 
  links: KnowledgeLink[] 
} => {
  const lines = csvText.trim().split('\n');
  const nodeMap = new Map<string, KnowledgeNode>();
  const links: KnowledgeLink[] = [];

  lines.forEach((line, index) => {
    // 跳过空行
    if (!line.trim()) return;
    
    const parts = line.split(',');
    if (parts.length >= 5) {
      const sourceName = parts[0].trim();
      const sourceId = parts[1].trim();
      const relation = parts[2].trim();
      const targetName = parts[3].trim();
      const targetId = parts[4].trim();

      // 添加源节点
      if (!nodeMap.has(sourceId)) {
        nodeMap.set(sourceId, {
          id: sourceId,
          name: sourceName,
          level: getNodeLevel(sourceId),
          color: colors[hashCode(sourceId) % colors.length]
        });
      }

      // 添加目标节点
      if (!nodeMap.has(targetId)) {
        nodeMap.set(targetId, {
          id: targetId,
          name: targetName,
          level: getNodeLevel(targetId),
          color: colors[hashCode(targetId) % colors.length]
        });
      }

      // 添加连接
      links.push({
        source: sourceId,
        target: targetId,
        relation: relation
      });
    }
  });

  return { nodes: nodeMap, links };
};

// 获取节点的邻居
export const getNodeNeighbors = (
  centerId: string, 
  allLinks: KnowledgeLink[]
): { neighbors: Set<string>, relevantLinks: KnowledgeLink[] } => {
  const neighbors = new Set<string>();
  const relevantLinks: KnowledgeLink[] = [];

  const toId = (endpoint: any): string => {
    if (typeof endpoint === 'string') return endpoint;
    if (endpoint && typeof endpoint === 'object') {
      // d3.forceLink 会把 source/target 变成节点对象，优先读 id
      if ('id' in endpoint) return String((endpoint as any).id);
    }
    return String(endpoint);
  };

  allLinks.forEach((link: any) => {
    const s = toId(link.source);
    const t = toId(link.target);
    if (s === centerId) {
      neighbors.add(t);
      relevantLinks.push({ source: s, target: t, relation: link.relation });
    } else if (t === centerId) {
      neighbors.add(s);
      relevantLinks.push({ source: s, target: t, relation: link.relation });
    }
  });

  return { neighbors, relevantLinks };
};

// 构建以某个节点为中心的子图
export const buildCenteredSubgraph = (
  centerId: string,
  allNodes: Map<string, KnowledgeNode>,
  allLinks: KnowledgeLink[]
): GraphData => {
  const centerNode = allNodes.get(centerId);
  if (!centerNode) {
    return { nodes: [], links: [] };
  }

  const { neighbors, relevantLinks } = getNodeNeighbors(centerId, allLinks);
  
  const nodes: KnowledgeNode[] = [];
  
  // 添加中心节点
  nodes.push({
    ...centerNode,
    isCenter: true
  });

  // 添加邻居节点
  neighbors.forEach(neighborId => {
    const neighborNode = allNodes.get(neighborId);
    if (neighborNode) {
      nodes.push({
        ...neighborNode,
        isCenter: false
      });
    }
  });

  // 返回新的 links 副本，避免 d3 修改影响全局
  const linksCloned: KnowledgeLink[] = relevantLinks.map(l => ({
    source: l.source,
    target: l.target,
    relation: l.relation,
  }));

  return { nodes, links: linksCloned };
};

// 加载知识图谱数据的主函数
export const loadKnowledgeGraphData = async (): Promise<{
  nodes: Map<string, KnowledgeNode>,
  links: KnowledgeLink[]
}> => {
  try {
    // 尝试从后端API加载数据
    const response = await fetch('/api/knowledge-graph');
    if (response.ok) {
      const csvText = await response.text();
      return parseKnowledgeGraphCSV(csvText);
    }
  } catch (error) {
    console.warn('无法从API加载知识图谱数据，使用本地数据:', error);
  }

  // 使用硬编码的数据作为后备方案
  return loadFallbackData();
};

// 后备数据（基于您提供的CSV内容）
const loadFallbackData = (): {
  nodes: Map<string, KnowledgeNode>,
  links: KnowledgeLink[]
} => {
  const csvData = `4图论,k0,includes,ch14图的基本概念,k1
4图论,k0,includes,ch15欧拉图&哈密顿图,k2
4图论,k0,includes,ch16树,k3
4图论,k0,includes,ch17平面图,k4
4图论,k0,includes,ch18着色,k5
ch14图的基本概念,k1,includes,14.1图,k6
ch14图的基本概念,k1,includes,14.2通路与回路,k7
ch14图的基本概念,k1,includes,14.3图的连通性,k8
ch14图的基本概念,k1,includes,14.4图的矩阵表示,k9
ch14图的基本概念,k1,includes,14.5图的运算,k10
14.1图,k6,includes,图的定义,k11
14.1图,k6,includes,多重图与简单图,k12
14.1图,k6,includes,顶点的度数,k13
14.1图,k6,includes,图的同构(必要条件),k14
14.1图,k6,includes,n阶完全图（竞赛图）、k-正则图,k15
14.1图,k6,includes,子图,k16
14.1图,k6,includes,补图,k17
图的定义,k11,includes,图,k18
图的定义,k11,includes,n阶零图,k19
图的定义,k11,includes,平凡图,k20
多重图与简单图,k12,includes,多重图,k21
多重图与简单图,k12,includes,简单图,k22
顶点的度数,k13,includes,顶点的度数,k23
顶点的度数,k13,includes,握手定理,k24
图的同构(必要条件),k14,includes,图的同构,k25
n阶完全图（竞赛图）、k-正则图,k15,includes,n阶完全图$K_n$,k26
n阶完全图（竞赛图）、k-正则图,k15,includes,竞赛图,k27
n阶完全图（竞赛图）、k-正则图,k15,includes,k-正则图,k28
子图,k16,includes,子图,k29
子图,k16,includes,导出子图,k30
子图,k16,includes,生成子图,k44
补图,k17,includes,补图,k31
14.2通路与回路,k7,includes,通路,k32
14.2通路与回路,k7,includes,回路,k33
14.2通路与回路,k7,includes,简单通路,k34
14.2通路与回路,k7,includes,初等通路,k35
14.2通路与回路,k7,includes,简单回路,k36
14.2通路与回路,k7,includes,初等回路,k37
通路,k32,includes,通路,k38
回路,k33,includes,回路,k39
简单通路,k34,includes,简单通路,k40
初等通路,k35,includes,初等通路,k41
简单回路,k36,includes,简单回路,k42
初等回路,k37,includes,初等回路,k43
14.3图的连通性,k8,includes,连通,k45
14.3图的连通性,k8,includes,连通图,k46
14.3图的连通性,k8,includes,连通分支,k47
14.3图的连通性,k8,includes,距离,k48
14.3图的连通性,k8,includes,直径,k49
连通,k45,includes,连通,k50
连通图,k46,includes,连通图,k51
连通分支,k47,includes,连通分支,k52
距离,k48,includes,距离,k53
直径,k49,includes,直径,k54
ch15欧拉图&哈密顿图,k2,includes,15.1欧拉图,k55
ch15欧拉图&哈密顿图,k2,includes,15.2哈密顿图,k56
15.1欧拉图,k55,includes,欧拉通路,k57
15.1欧拉图,k55,includes,欧拉回路,k58
15.1欧拉图,k55,includes,欧拉图E,k90
15.1欧拉图,k55,includes,半欧拉图,k91
15.1欧拉图,k55,includes,欧拉图判别方法,k92
欧拉通路,k57,includes,欧拉通路,k93
欧拉回路,k58,includes,欧拉回路,k94
15.2哈密顿图,k56,includes,哈密顿通路,k95
15.2哈密顿图,k56,includes,哈密顿回路,k96
15.2哈密顿图,k56,includes,哈密顿图H,k103
15.2哈密顿图,k56,includes,半哈密顿图,k104
15.2哈密顿图,k56,includes,哈密顿图判别方法,k105
哈密顿通路,k95,includes,哈密顿通路,k97
哈密顿回路,k96,includes,哈密顿回路,k98
ch16树,k3,includes,16.1树的定义,k99
ch16树,k3,includes,16.2生成树,k100
16.1树的定义,k99,includes,树,k101
16.1树的定义,k99,includes,森林,k102
树,k101,includes,树,k106
森林,k102,includes,森林,k107
16.2生成树,k100,includes,生成树,k108
生成树,k108,includes,生成树,k109
ch17平面图,k4,includes,17.1平面图的定义,k110
ch17平面图,k4,includes,17.2平面图的判别,k111
17.1平面图的定义,k110,includes,平面图定义,k152
17.1平面图的定义,k110,includes,极大平面图,k154
17.1平面图的定义,k110,includes,极小非平面图,k155
平面图定义,k152,includes,平面图,k153
17.2平面图的判别,k111,includes,连通平面图欧拉公式,k166
17.2平面图的判别,k111,includes,简单平面图性质,k167
17.2平面图的判别,k111,includes,平面图判断方法,k175
连通平面图欧拉公式,k166,includes,连通平面图欧拉公式,k168
简单平面图性质,k167,includes,简单平面图性质,k169
平面图判断方法,k175,includes,Kuratowski定理,k176
平面图判断方法,k175,includes,同胚,k177
ch18着色,k5,includes,18.1点着色,k178
ch18着色,k5,includes,18.2边着色,k179
ch18着色,k5,includes,18.3二部图的匹配,k184
18.1点着色,k178,includes,点独立集与点独立数$\\beta_0$,k189
18.1点着色,k178,includes,点覆盖集与点覆盖数$\\alpha_0$,k190
18.1点着色,k178,includes,色数$\\chi(G)$,k211
点独立集与点独立数$\\beta_0$,k189,includes,点独立集,k191
点独立集与点独立数$\\beta_0$,k189,includes,点独立数$\\beta_0$,k192
点覆盖集与点覆盖数$\\alpha_0$,k190,includes,点覆盖集,k193
点覆盖集与点覆盖数$\\alpha_0$,k190,includes,点覆盖数$\\alpha_0$,k194
色数$\\chi(G)$,k211,includes,色数$\\chi(G)$,k212
色数$\\chi(G)$,k211,includes,面色数$\\chi^*(G)$,k214
18.2边着色,k179,includes,边独立集与边独立数$\\beta_1$,k197
18.2边着色,k179,includes,边覆盖集与边覆盖数$\\alpha_1$,k196
18.2边着色,k179,includes,边色数$\\chi'(G)$,k216
边独立集与边独立数$\\beta_1$,k197,includes,边独立集,k198
边独立集与边独立数$\\beta_1$,k197,includes,边独立数$\\beta_1$,k200
边覆盖集与边覆盖数$\\alpha_1$,k196,includes,边覆盖集,k201
边覆盖集与边覆盖数$\\alpha_1$,k196,includes,边覆盖数$\\alpha_1$,k202
边色数$\\chi'(G)$,k216,includes,边色数$\\chi'(G)$,k217
18.3二部图的匹配,k184,includes,匹配M中的相关概念,k199
18.3二部图的匹配,k184,includes,完美匹配,k204
18.3二部图的匹配,k184,includes,完备匹配,k207
匹配M中的相关概念,k199,includes,匹配,k203
完美匹配,k204,includes,完美匹配,k205
完备匹配,k207,includes,完备匹配,k208`;

  return parseKnowledgeGraphCSV(csvData);
};
