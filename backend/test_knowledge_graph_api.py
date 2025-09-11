#!/usr/bin/env python3
"""
测试知识图谱API
验证知识图谱数据API是否正常工作
"""

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:5000'

def test_knowledge_graph_api():
    """测试知识图谱API"""
    print("🧪 测试知识图谱API")
    print("=" * 50)
    
    # 1. 检查后端服务
    print("\n1. 检查后端服务状态")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ 后端服务正常运行")
        else:
            print("❌ 后端服务异常")
            return
    except:
        print("❌ 无法连接到后端服务")
        return
    
    # 2. 测试知识图谱API
    print("\n2. 测试知识图谱API")
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge-graph")
        if response.status_code == 200:
            csv_content = response.text
            print("✅ 知识图谱API调用成功")
            
            # 解析CSV内容
            lines = csv_content.strip().split('\n')
            print(f"   获取到 {len(lines)} 行数据")
            
            # 显示前几行数据
            print("\n📊 知识图谱数据预览:")
            for i, line in enumerate(lines[:5], 1):
                parts = line.split(',')
                if len(parts) >= 5:
                    source_name = parts[0].strip()
                    source_id = parts[1].strip()
                    relation = parts[2].strip()
                    target_name = parts[3].strip()
                    target_id = parts[4].strip()
                    print(f"   {i}. {source_name}({source_id}) --{relation}--> {target_name}({target_id})")
            
            # 统计节点和连接
            nodes = set()
            links = []
            
            for line in lines:
                if not line.strip():
                    continue
                parts = line.split(',')
                if len(parts) >= 5:
                    source_id = parts[1].strip()
                    target_id = parts[4].strip()
                    relation = parts[2].strip()
                    
                    nodes.add(source_id)
                    nodes.add(target_id)
                    links.append({
                        'source': source_id,
                        'target': target_id,
                        'relation': relation
                    })
            
            print(f"\n📈 知识图谱统计:")
            print(f"   节点数量: {len(nodes)}")
            print(f"   连接数量: {len(links)}")
            
            # 显示根节点
            root_nodes = [node for node in nodes if node == 'k0']
            if root_nodes:
                print(f"   根节点: {root_nodes}")
            
            # 显示一些关键节点
            key_nodes = [node for node in nodes if node in ['k1', 'k2', 'k3', 'k4', 'k5']]
            if key_nodes:
                print(f"   主要章节节点: {key_nodes}")
            
        else:
            print(f"❌ 知识图谱API调用失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 知识图谱API调用异常: {e}")
        return
    
    # 3. 测试前端数据格式兼容性
    print("\n3. 测试前端数据格式兼容性")
    try:
        # 模拟前端解析逻辑
        lines = csv_content.strip().split('\n')
        node_map = {}
        links = []
        
        for line in lines:
            if not line.strip():
                continue
            parts = line.split(',')
            if len(parts) >= 5:
                source_name = parts[0].strip()
                source_id = parts[1].strip()
                relation = parts[2].strip()
                target_name = parts[3].strip()
                target_id = parts[4].strip()
                
                # 添加节点
                if source_id not in node_map:
                    node_map[source_id] = {
                        'id': source_id,
                        'name': source_name,
                        'level': 0
                    }
                
                if target_id not in node_map:
                    node_map[target_id] = {
                        'id': target_id,
                        'name': target_name,
                        'level': 0
                    }
                
                # 添加连接
                links.append({
                    'source': source_id,
                    'target': target_id,
                    'relation': relation
                })
        
        print(f"✅ 前端数据解析成功")
        print(f"   解析节点数: {len(node_map)}")
        print(f"   解析连接数: {len(links)}")
        
        # 检查关键节点
        if 'k0' in node_map:
            print(f"   根节点信息: {node_map['k0']}")
        
        # 检查连接关系
        root_connections = [link for link in links if link['source'] == 'k0' or link['target'] == 'k0']
        print(f"   根节点连接数: {len(root_connections)}")
        
    except Exception as e:
        print(f"❌ 前端数据解析异常: {e}")
        return
    
    # 4. 测试知识图谱可视化所需的数据结构
    print("\n4. 测试可视化数据结构")
    try:
        # 模拟构建以k0为中心的子图
        center_id = 'k0'
        center_node = node_map.get(center_id)
        
        if center_node:
            # 找到与中心节点直接相连的节点
            neighbors = set()
            relevant_links = []
            
            for link in links:
                if link['source'] == center_id:
                    neighbors.add(link['target'])
                    relevant_links.append(link)
                elif link['target'] == center_id:
                    neighbors.add(link['source'])
                    relevant_links.append(link)
            
            # 构建子图
            subgraph_nodes = [center_node]
            for neighbor_id in neighbors:
                if neighbor_id in node_map:
                    subgraph_nodes.append(node_map[neighbor_id])
            
            print(f"✅ 子图构建成功")
            print(f"   中心节点: {center_node['name']} ({center_id})")
            print(f"   邻居节点数: {len(neighbors)}")
            print(f"   子图节点数: {len(subgraph_nodes)}")
            print(f"   子图连接数: {len(relevant_links)}")
            
            # 显示邻居节点
            print(f"   邻居节点:")
            for neighbor_id in list(neighbors)[:5]:  # 只显示前5个
                neighbor_node = node_map.get(neighbor_id)
                if neighbor_node:
                    print(f"     - {neighbor_node['name']} ({neighbor_id})")
            
        else:
            print("❌ 未找到根节点k0")
            
    except Exception as e:
        print(f"❌ 可视化数据结构测试异常: {e}")
        return
    
    print("\n🎉 知识图谱API测试完成！")
    print("=" * 50)

def main():
    """主函数"""
    test_knowledge_graph_api()

if __name__ == '__main__':
    main()

