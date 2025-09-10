#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建有意义的知识点嵌入
基于知识图谱的拓扑结构，让相关知识点在向量空间中更接近
"""

import csv
import numpy as np
import networkx as nx
from sklearn.manifold import MDS
from sklearn.decomposition import PCA
from collections import defaultdict
import pandas as pd

def load_knowledge_graph(csv_path):
    """加载知识图谱"""
    G = nx.DiGraph()
    kp_names = {}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            kp1_id = row['kp1_id']
            kp2_id = row['kp2_id']
            kp1_name = row['kp1_name']
            kp2_name = row['kp2_name']
            relation = row['relation']
            
            # 记录知识点名称
            kp_names[kp1_id] = kp1_name
            kp_names[kp2_id] = kp2_name
            
            # 添加边，权重根据关系类型设置
            if relation == "is_prerequisite_for":
                weight = 1.0  # 前置关系权重较低（距离较近）
            elif relation == "is_related_to":
                weight = 1.5  # 相关关系权重稍高
            else:
                weight = 2.0
            
            G.add_edge(kp1_id, kp2_id, weight=weight, relation=relation)
            # 对于相关关系，添加双向边
            if relation == "is_related_to":
                G.add_edge(kp2_id, kp1_id, weight=weight, relation=relation)
    
    return G, kp_names

def create_hierarchical_embeddings(G, kp_names, dim=50, seed=42):
    """
    基于知识图谱层次结构创建嵌入
    """
    np.random.seed(seed)
    kp_ids = list(G.nodes())
    n_kps = len(kp_ids)
    
    # 1. 计算知识点的层次深度（从基础到高级）
    def get_depth(node, visited=None):
        if visited is None:
            visited = set()
        if node in visited:
            return 0
        visited.add(node)
        
        predecessors = list(G.predecessors(node))
        if not predecessors:
            return 0
        else:
            return 1 + max([get_depth(pred, visited.copy()) for pred in predecessors])
    
    depths = {kp: get_depth(kp) for kp in kp_ids}
    max_depth = max(depths.values())
    
    print("知识点层次结构:")
    for depth in range(max_depth + 1):
        kps_at_depth = [kp for kp, d in depths.items() if d == depth]
        print(f"  层次 {depth}: {[f'{kp}({kp_names[kp]})' for kp in kps_at_depth]}")
    
    # 2. 初始化嵌入矩阵
    embeddings = np.random.normal(0, 0.1, (n_kps, dim))
    kp_to_idx = {kp: i for i, kp in enumerate(kp_ids)}
    
    # 3. 基于层次结构调整第一个维度（表示知识难度/层次）
    for kp, depth in depths.items():
        idx = kp_to_idx[kp]
        # 第一维表示知识层次，从-1（基础）到1（高级）
        embeddings[idx, 0] = -1 + 2 * (depth / max_depth) if max_depth > 0 else 0
    
    # 4. 基于图结构调整其他维度
    # 使用图的谱嵌入方法
    try:
        # 计算拉普拉斯矩阵
        L = nx.normalized_laplacian_matrix(G.to_undirected(), nodelist=kp_ids)
        L_dense = L.toarray()
        
        # 特征值分解
        eigenvals, eigenvecs = np.linalg.eigh(L_dense)
        
        # 使用前dim-1个特征向量作为嵌入的其余维度
        spectral_dim = min(dim-1, n_kps-1)
        embeddings[:, 1:spectral_dim+1] = eigenvecs[:, 1:spectral_dim+1]
    except:
        print("谱嵌入失败，使用随机初始化")
    
    # 5. 基于直接连接关系进行局部调整
    learning_rate = 0.01
    iterations = 1000
    
    for iter in range(iterations):
        for kp1, kp2, data in G.edges(data=True):
            idx1, idx2 = kp_to_idx[kp1], kp_to_idx[kp2]
            
            # 计算当前距离
            current_dist = np.linalg.norm(embeddings[idx1] - embeddings[idx2])
            target_dist = data['weight']
            
            # 梯度下降调整
            if current_dist > 0:
                direction = (embeddings[idx2] - embeddings[idx1]) / current_dist
                delta = learning_rate * (current_dist - target_dist) * direction
                
                # 不调整第一维（保持层次结构）
                delta[0] = 0
                
                embeddings[idx1] += delta * 0.5
                embeddings[idx2] -= delta * 0.5
    
    # 6. 归一化
    for i in range(n_kps):
        norm = np.linalg.norm(embeddings[i])
        if norm > 0:
            embeddings[i] /= norm
    
    return {kp_ids[i]: embeddings[i] for i in range(n_kps)}

def create_cluster_based_embeddings(G, kp_names, dim=50, seed=42):
    """
    基于知识聚类创建嵌入
    """
    np.random.seed(seed)
    kp_ids = list(G.nodes())
    
    # 定义知识点聚类（基于领域相关性）
    clusters = {
        "基础理论": ["K1", "K2", "K3"],  # 集合、关系、图基本概念
        "图表示与度": ["K4", "K8", "K9"],  # 图表示、度概念、握手定理
        "图遍历与连通": ["K5", "K6", "K7"],  # 遍历、连通性、强连通分量
        "子图与树": ["K10", "K11", "K12", "K13"],  # 子图、树、生成树、最小生成树
        "路径与特殊图": ["K14", "K15", "K16"],  # 路径、欧拉图、哈密顿图
        "最短路径算法": ["K17", "K18", "K19"],  # 最短路径、Dijkstra、Floyd
        "二分图与匹配": ["K20", "K21", "K22"],  # 二分图、匹配、最大匹配
        "平面图与着色": ["K23", "K24", "K25", "K26"]  # 平面图、欧拉公式、着色、四色定理
    }
    
    embeddings = {}
    cluster_centers = {}
    
    # 为每个聚类生成中心点
    n_clusters = len(clusters)
    center_dim = min(10, dim)  # 用前10维表示聚类信息
    
    for i, (cluster_name, _) in enumerate(clusters.items()):
        # 在前center_dim维度中为每个聚类分配不同的方向
        center = np.random.normal(0, 0.3, dim)
        
        # 在聚类维度中设置主要方向
        if i < center_dim:
            center[i] = 1.0  # 在第i维设置主要特征
        
        cluster_centers[cluster_name] = center
    
    print("知识点聚类:")
    for cluster_name, kp_list in clusters.items():
        kp_info = []
        for kp in kp_list:
            if kp in kp_names:
                kp_info.append(f'{kp}({kp_names[kp]})')
        print(f"  {cluster_name}: {kp_info}")
    
    # 为每个知识点生成嵌入
    for cluster_name, kp_list in clusters.items():
        cluster_center = cluster_centers[cluster_name]
        
        for kp in kp_list:
            if kp in kp_ids:
                # 在聚类中心周围添加噪声
                noise = np.random.normal(0, 0.2, dim)
                embedding = cluster_center + noise
                
                # 归一化
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding /= norm
                
                embeddings[kp] = embedding
    
    # 处理未分类的知识点
    for kp in kp_ids:
        if kp not in embeddings:
            embedding = np.random.normal(0, 0.1, dim)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding /= norm
            embeddings[kp] = embedding
    
    return embeddings

def analyze_embedding_quality(embeddings, G, kp_names):
    """分析嵌入质量"""
    from sklearn.metrics.pairwise import cosine_similarity
    
    print("\n=== 嵌入质量分析 ===")
    
    # 1. 分析相关关系的相似度
    related_pairs = []
    prereq_pairs = []
    
    for kp1, kp2, data in G.edges(data=True):
        if data['relation'] == 'is_related_to':
            related_pairs.append((kp1, kp2))
        elif data['relation'] == 'is_prerequisite_for':
            prereq_pairs.append((kp1, kp2))
    
    if related_pairs:
        related_similarities = []
        for kp1, kp2 in related_pairs:
            sim = cosine_similarity([embeddings[kp1]], [embeddings[kp2]])[0][0]
            related_similarities.append(sim)
            print(f"相关关系 {kp_names[kp1]} <-> {kp_names[kp2]}: {sim:.3f}")
        
        print(f"相关关系平均相似度: {np.mean(related_similarities):.3f}")
    
    if prereq_pairs:
        prereq_similarities = []
        for kp1, kp2 in prereq_pairs[:5]:  # 只显示前5个
            sim = cosine_similarity([embeddings[kp1]], [embeddings[kp2]])[0][0]
            prereq_similarities.append(sim)
            print(f"前置关系 {kp_names[kp1]} -> {kp_names[kp2]}: {sim:.3f}")
        
        print(f"前置关系平均相似度: {np.mean(prereq_similarities):.3f}")
    
    # 2. 分析随机对的相似度作为对照
    random_similarities = []
    kp_list = list(embeddings.keys())
    for _ in range(10):
        kp1, kp2 = np.random.choice(kp_list, 2, replace=False)
        if not G.has_edge(kp1, kp2) and not G.has_edge(kp2, kp1):
            sim = cosine_similarity([embeddings[kp1]], [embeddings[kp2]])[0][0]
            random_similarities.append(sim)
    
    if random_similarities:
        print(f"随机对平均相似度: {np.mean(random_similarities):.3f}")

def save_embeddings(embeddings, output_path):
    """保存嵌入到CSV文件"""
    kp_ids = sorted(embeddings.keys())
    dim = len(embeddings[kp_ids[0]])
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        # 写入标题行
        header = ['kp_id'] + [f'dim_{i}' for i in range(dim)]
        writer.writerow(header)
        
        # 写入数据
        for kp_id in kp_ids:
            row = [kp_id] + list(embeddings[kp_id])
            writer.writerow(row)
    
    print(f"嵌入已保存到: {output_path}")

def main():
    # 加载知识图谱
    kg_path = '/home/dzz/KGsystem/transE/recommend/knowledge_graph.csv'
    G, kp_names = load_knowledge_graph(kg_path)
    
    print(f"加载知识图谱: {len(G.nodes())} 个知识点, {len(G.edges())} 条关系")
    
    # 方法1: 基于层次结构的嵌入
    print("\n=== 创建层次结构嵌入 ===")
    hierarchical_embeddings = create_hierarchical_embeddings(G, kp_names, dim=50)
    analyze_embedding_quality(hierarchical_embeddings, G, kp_names)
    
    # 方法2: 基于聚类的嵌入
    print("\n=== 创建聚类嵌入 ===")
    cluster_embeddings = create_cluster_based_embeddings(G, kp_names, dim=50)
    analyze_embedding_quality(cluster_embeddings, G, kp_names)
    
    # 选择更好的方法（这里选择聚类方法，因为它更符合教学直觉）
    chosen_embeddings = cluster_embeddings
    
    # 保存结果
    output_path = '/home/dzz/KGsystem/transE/recommend/embeddings_meaningful.csv'
    save_embeddings(chosen_embeddings, output_path)
    
    print(f"\n生成的有意义嵌入已保存到: {output_path}")
    print("建议将其重命名为 embeddings.csv 来替换随机嵌入")

if __name__ == '__main__':
    main()
