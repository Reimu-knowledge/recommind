#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱可视化工具
支持多种可视化方式和交互功能
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Tuple, Optional
import json
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class KGVisualizer:
    """知识图谱可视化器"""
    
    def __init__(self, kg_file: str):
        """
        初始化可视化器
        
        Args:
            kg_file: 知识图谱CSV文件路径
        """
        self.kg_file = kg_file
        self.kg_data = None
        self.graph = None
        self.load_knowledge_graph()
        
    def load_knowledge_graph(self):
        """加载知识图谱数据"""
        try:
            self.kg_data = pd.read_csv(self.kg_file)
            print(f"成功加载知识图谱，包含 {len(self.kg_data)} 条三元组")
            self.build_graph()
        except Exception as e:
            print(f"加载知识图谱失败: {e}")
            raise
    
    def build_graph(self):
        """构建NetworkX图对象"""
        self.graph = nx.DiGraph()
        
        for _, row in self.kg_data.iterrows():
            self.graph.add_edge(
                row['subject'],
                row['object'],
                relation=row['predicate'],
                source=row.get('source', 'unknown')
            )
        
        print(f"图对象构建完成，包含 {len(self.graph.nodes())} 个节点和 {len(self.graph.edges())} 条边")
    
    def analyze_graph_structure(self) -> Dict:
        """分析图结构"""
        if self.graph is None:
            return {}
        
        # 计算基本统计信息
        analysis = {
            "total_nodes": len(self.graph.nodes()),
            "total_edges": len(self.graph.edges()),
            "avg_degree": np.mean([d for n, d in self.graph.degree()]),
            "density": nx.density(self.graph),
            "is_connected": nx.is_weakly_connected(self.graph),
            "num_components": nx.number_weakly_connected_components(self.graph),
            "avg_clustering": nx.average_clustering(self.graph.to_undirected()),
            "diameter": nx.diameter(self.graph.to_undirected()) if nx.is_connected(self.graph.to_undirected()) else "N/A"
        }
        
        return analysis
    
    def create_matplotlib_visualization(self, max_nodes: int = 50, figsize: Tuple[int, int] = (20, 15)):
        """创建matplotlib可视化"""
        if self.graph is None:
            print("图对象未构建")
            return
        
        # 如果节点太多，选择子图
        if len(self.graph.nodes()) > max_nodes:
            # 选择度最高的节点
            top_nodes = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph([node for node, _ in top_nodes])
            print(f"选择前 {max_nodes} 个高连接度节点进行可视化")
        else:
            subgraph = self.graph
        
        plt.figure(figsize=figsize)
        
        # 使用spring布局
        pos = nx.spring_layout(subgraph, k=3, iterations=50, seed=42)
        
        # 根据节点度设置节点大小
        node_sizes = [subgraph.degree(node) * 200 + 500 for node in subgraph.nodes()]
        
        # 根据节点度设置节点颜色
        degrees = [subgraph.degree(node) for node in subgraph.nodes()]
        node_colors = plt.cm.viridis(np.array(degrees) / max(degrees))
        
        # 绘制节点
        nx.draw_networkx_nodes(subgraph, pos, 
                              node_size=node_sizes,
                              node_color=node_colors,
                              alpha=0.8)
        
        # 绘制边
        nx.draw_networkx_edges(subgraph, pos, 
                              edge_color='gray',
                              arrows=True, 
                              arrowsize=20,
                              alpha=0.6)
        
        # 绘制节点标签
        nx.draw_networkx_labels(subgraph, pos, 
                               font_size=8, 
                               font_family='SimHei',
                               font_weight='bold')
        
        # 绘制边标签（关系）
        edge_labels = nx.get_edge_attributes(subgraph, 'relation')
        nx.draw_networkx_edge_labels(subgraph, pos, 
                                    edge_labels=edge_labels, 
                                    font_size=6,
                                    font_family='SimHei')
        
        plt.title("图论知识图谱可视化 (Matplotlib)", fontsize=20, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # 添加图例
        self._add_legend(degrees)
        
        plt.show()
    
    def _add_legend(self, degrees):
        """添加图例"""
        if not degrees:
            return
        
        # 创建颜色条
        sm = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=min(degrees), vmax=max(degrees)))
        sm.set_array([])
        
        # 添加颜色条
        cbar = plt.colorbar(sm, ax=plt.gca(), shrink=0.8, aspect=30)
        cbar.set_label('节点连接度', fontsize=12)
        cbar.ax.tick_params(labelsize=10)
    
    def create_plotly_visualization(self, max_nodes: int = 100):
        """创建Plotly交互式可视化"""
        if self.graph is None:
            print("图对象未构建")
            return
        
        # 如果节点太多，选择子图
        if len(self.graph.nodes()) > max_nodes:
            top_nodes = sorted(self.graph.degree(), key=lambda x: x[1], reverse=True)[:max_nodes]
            subgraph = self.graph.subgraph([node for node, _ in top_nodes])
            print(f"选择前 {max_nodes} 个高连接度节点进行可视化")
        else:
            subgraph = self.graph
        
        # 使用spring布局
        pos = nx.spring_layout(subgraph, k=3, iterations=50, seed=42)
        
        # 准备节点数据
        node_x = [pos[node][0] for node in subgraph.nodes()]
        node_y = [pos[node][1] for node in subgraph.nodes()]
        node_text = [f"{node}<br>连接度: {subgraph.degree(node)}" for node in subgraph.nodes()]
        node_sizes = [subgraph.degree(node) * 10 + 20 for node in subgraph.nodes()]
        node_colors = [subgraph.degree(node) for node in subgraph.nodes()]
        
        # 准备边数据
        edge_x = []
        edge_y = []
        edge_text = []
        
        for edge in subgraph.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_text.append(edge[2].get('relation', 'unknown'))
        
        # 创建图形
        fig = go.Figure()
        
        # 添加边
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=1, color='gray'),
            hoverinfo='none',
            showlegend=False
        ))
        
        # 添加节点
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="节点连接度")
            ),
            text=[node[:10] + '...' if len(node) > 10 else node for node in subgraph.nodes()],
            textposition="top center",
            textfont=dict(size=8),
            hovertext=node_text,
            hoverinfo='text',
            name='节点'
        ))
        
        # 更新布局
        fig.update_layout(
            title={
                'text': "图论知识图谱交互式可视化 (Plotly)",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )
        
        fig.show()
    
    def create_hierarchical_visualization(self, max_depth: int = 3):
        """创建层次化可视化"""
        if self.graph is None:
            print("图对象未构建")
            return
        
        # 从根节点开始构建层次结构
        root_nodes = [node for node, in_degree in self.graph.in_degree() if in_degree == 0]
        if not root_nodes:
            root_nodes = ['图论']  # 默认根节点
        
        # 构建层次结构
        hierarchy = self._build_hierarchy(root_nodes[0], max_depth)
        
        # 创建Plotly树形图
        fig = go.Figure(go.Treemap(
            labels=list(hierarchy.keys()),
            parents=[hierarchy.get(label, '') for label in hierarchy.keys()],
            values=[self.graph.degree(label) for label in hierarchy.keys()],
            textinfo="label+value",
            hovertemplate="<b>%{label}</b><br>连接度: %{value}<extra></extra>"
        ))
        
        fig.update_layout(
            title={
                'text': "图论知识图谱层次结构可视化",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20}
            },
            width=1200,
            height=800
        )
        
        fig.show()
    
    def _build_hierarchy(self, root: str, max_depth: int, current_depth: int = 0) -> Dict:
        """构建层次结构"""
        if current_depth >= max_depth:
            return {}
        
        hierarchy = {}
        neighbors = list(self.graph.neighbors(root))
        
        for neighbor in neighbors[:10]:  # 限制每个节点的子节点数量
            hierarchy[neighbor] = root
            # 递归构建子层次
            sub_hierarchy = self._build_hierarchy(neighbor, max_depth, current_depth + 1)
            hierarchy.update(sub_hierarchy)
        
        return hierarchy
    
    def create_relation_analysis_chart(self):
        """创建关系分析图表"""
        if self.kg_data is None:
            print("知识图谱数据未加载")
            return
        
        # 统计关系类型
        relation_counts = self.kg_data['predicate'].value_counts()
        
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('关系类型分布', '前20个关系类型', '关系类型词云', '实体连接度分布'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "histogram"}]]
        )
        
        # 1. 饼图：关系类型分布
        fig.add_trace(
            go.Pie(labels=relation_counts.index[:10], values=relation_counts.values[:10]),
            row=1, col=1
        )
        
        # 2. 柱状图：前20个关系类型
        fig.add_trace(
            go.Bar(x=relation_counts.index[:20], y=relation_counts.values[:20]),
            row=1, col=2
        )
        
        # 3. 散点图：关系类型词云效果
        fig.add_trace(
            go.Scatter(
                x=np.random.rand(len(relation_counts)),
                y=np.random.rand(len(relation_counts)),
                mode='text',
                text=relation_counts.index,
                textfont=dict(size=relation_counts.values / relation_counts.values.max() * 20 + 10),
                hovertext=[f"{rel}: {count}" for rel, count in relation_counts.items()],
                hoverinfo='text'
            ),
            row=2, col=1
        )
        
        # 4. 直方图：实体连接度分布
        if self.graph:
            degrees = [self.graph.degree(node) for node in self.graph.nodes()]
            fig.add_trace(
                go.Histogram(x=degrees, nbinsx=20),
                row=2, col=2
            )
        
        # 更新布局
        fig.update_layout(
            title="知识图谱关系分析",
            height=800,
            showlegend=False
        )
        
        fig.show()
    
    def create_entity_network_analysis(self):
        """创建实体网络分析"""
        if self.graph is None:
            print("图对象未构建")
            return
        
        # 计算网络指标
        analysis = self.analyze_graph_structure()
        
        # 计算中心性指标
        centrality = nx.degree_centrality(self.graph)
        betweenness = nx.betweenness_centrality(self.graph)
        closeness = nx.closeness_centrality(self.graph)
        
        # 获取前20个重要节点
        top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 创建分析图表
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('节点度中心性', '节点介数中心性', '节点接近中心性', '网络指标概览'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "indicator"}]]
        )
        
        # 1. 度中心性
        fig.add_trace(
            go.Bar(x=[node for node, _ in top_nodes], y=[cent for _, cent in top_nodes]),
            row=1, col=1
        )
        
        # 2. 介数中心性
        top_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:20]
        fig.add_trace(
            go.Bar(x=[node for node, _ in top_betweenness], y=[cent for _, cent in top_betweenness]),
            row=1, col=2
        )
        
        # 3. 接近中心性
        top_closeness = sorted(closeness.items(), key=lambda x: x[1], reverse=True)[:20]
        fig.add_trace(
            go.Bar(x=[node for node, _ in top_closeness], y=[cent for _, cent in top_closeness]),
            row=2, col=1
        )
        
        # 4. 网络指标概览
        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=analysis.get('avg_clustering', 0),
                title={'text': "平均聚类系数"},
                gauge={'axis': {'range': [None, 1]},
                       'bar': {'color': "darkblue"},
                       'steps': [{'range': [0, 0.3], 'color': "lightgray"},
                                {'range': [0.3, 0.7], 'color': "gray"},
                                {'range': [0.7, 1], 'color': "darkgray"}],
                       'threshold': {'line': {'color': "red", 'width': 4},
                                   'thickness': 0.75, 'value': 0.5}}
            ),
            row=2, col=2
        )
        
        # 更新布局
        fig.update_layout(
            title="知识图谱网络分析",
            height=800,
            showlegend=False
        )
        
        fig.show()
    
    def export_visualization_data(self, output_file: str = "visualization_data.json"):
        """导出可视化数据"""
        if self.graph is None:
            print("图对象未构建")
            return
        
        # 准备导出数据
        export_data = {
            "graph_info": {
                "total_nodes": len(self.graph.nodes()),
                "total_edges": len(self.graph.edges()),
                "density": nx.density(self.graph),
                "is_connected": nx.is_weakly_connected(self.graph),
                "num_components": nx.number_weakly_connected_components(self.graph)
            },
            "nodes": [
                {
                    "id": node,
                    "degree": self.graph.degree(node),
                    "in_degree": self.graph.in_degree(node),
                    "out_degree": self.graph.out_degree(node)
                }
                for node in self.graph.nodes()
            ],
            "edges": [
                {
                    "source": edge[0],
                    "target": edge[1],
                    "relation": edge[2].get('relation', 'unknown'),
                    "source_type": edge[2].get('source', 'unknown')
                }
                for edge in self.graph.edges(data=True)
            ],
            "top_nodes": sorted(
                [(node, self.graph.degree(node)) for node in self.graph.nodes()],
                key=lambda x: x[1],
                reverse=True
            )[:20]
        }
        
        # 保存到文件
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"可视化数据已导出到: {output_file}")

def main():
    """主函数"""
    try:
        # 创建可视化器
        visualizer = KGVisualizer("optimized_knowledge_graph.csv")
        
        print("=== 知识图谱可视化工具 ===")
        print("1. 分析图结构...")
        analysis = visualizer.analyze_graph_structure()
        print("图结构分析结果:")
        for key, value in analysis.items():
            print(f"  - {key}: {value}")
        
        print("\n2. 创建matplotlib可视化...")
        visualizer.create_matplotlib_visualization(max_nodes=60)
        
        print("\n3. 创建Plotly交互式可视化...")
        visualizer.create_plotly_visualization(max_nodes=80)
        
        print("\n4. 创建层次化可视化...")
        visualizer.create_hierarchical_visualization(max_depth=3)
        
        print("\n5. 创建关系分析图表...")
        visualizer.create_relation_analysis_chart()
        
        print("\n6. 创建实体网络分析...")
        visualizer.create_entity_network_analysis()
        
        print("\n7. 导出可视化数据...")
        visualizer.export_visualization_data()
        
        print("\n=== 所有可视化完成 ===")
        
    except Exception as e:
        print(f"可视化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
