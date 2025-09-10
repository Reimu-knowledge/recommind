#!/usr/bin/env python3
"""
调试知识点映射和题目匹配问题
"""

import json
import csv
import os

def load_knowledge_points_mapping():
    """加载知识点映射"""
    knowledge_points_mapping = {}
    try:
        knowledge_points_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'formatted_nodes.csv')
        with open(knowledge_points_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                knowledge_points_mapping[row['name']] = row['id']
        
        print(f"✅ 知识点映射加载成功，共{len(knowledge_points_mapping)}个知识点")
        print("前5个映射关系:")
        for i, (kp_id, kp_name) in enumerate(list(knowledge_points_mapping.items())[:5]):
            print(f"  {i+1}. {kp_id} -> {kp_name}")
        
        return knowledge_points_mapping
    except Exception as e:
        print(f"❌ 知识点映射加载失败: {e}")
        return {}

def load_questions_data():
    """加载题目数据"""
    questions_data = {}
    try:
        questions_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'question.json')
        with open(questions_path, 'r', encoding='utf-8') as f:
            questions_json = json.load(f)
            for question in questions_json['questions']:
                questions_data[question['qid']] = question
        
        print(f"✅ 题目数据加载成功，共{len(questions_data)}道题目")
        return questions_data
    except Exception as e:
        print(f"❌ 题目数据加载失败: {e}")
        return {}

def analyze_knowledge_points_in_questions(questions_data):
    """分析题目中的知识点分布"""
    all_knowledge_points = set()
    knowledge_point_count = {}
    
    for qid, question in questions_data.items():
        knowledge_points = question.get('knowledge_points', {})
        for kp_id in knowledge_points.keys():
            all_knowledge_points.add(kp_id)
            knowledge_point_count[kp_id] = knowledge_point_count.get(kp_id, 0) + 1
    
    print(f"\n📊 题目中的知识点分析:")
    print(f"   总知识点数量: {len(all_knowledge_points)}")
    print(f"   前10个知识点及其题目数量:")
    
    # 按题目数量排序
    sorted_kps = sorted(knowledge_point_count.items(), key=lambda x: x[1], reverse=True)
    for i, (kp_id, count) in enumerate(sorted_kps[:10]):
        print(f"   {i+1}. {kp_id}: {count}道题目")
    
    return all_knowledge_points, knowledge_point_count

def test_specific_knowledge_point(knowledge_point_id, questions_data, knowledge_points_mapping):
    """测试特定知识点的题目匹配"""
    print(f"\n🔍 测试知识点 {knowledge_point_id}:")
    
    # 获取知识点名称
    kp_name = knowledge_points_mapping.get(knowledge_point_id, knowledge_point_id)
    print(f"   知识点名称: {kp_name}")
    
    # 查找包含该知识点的题目
    related_questions = []
    for qid, question in questions_data.items():
        if knowledge_point_id in question.get('knowledge_points', {}):
            related_questions.append({
                'qid': qid,
                'content': question['content'][:50] + '...',
                'knowledge_points': question['knowledge_points']
            })
    
    print(f"   匹配到的题目数量: {len(related_questions)}")
    
    if related_questions:
        print("   前5道题目:")
        for i, q in enumerate(related_questions[:5]):
            print(f"     {i+1}. {q['qid']}: {q['content']}")
            print(f"        知识点权重: {q['knowledge_points']}")
    else:
        print("   ❌ 没有找到相关题目")
    
    return related_questions

def main():
    """主函数"""
    print("🚀 开始调试知识点映射和题目匹配问题")
    print("=" * 60)
    
    # 1. 加载知识点映射
    knowledge_points_mapping = load_knowledge_points_mapping()
    
    # 2. 加载题目数据
    questions_data = load_questions_data()
    
    # 3. 分析题目中的知识点分布
    all_knowledge_points, knowledge_point_count = analyze_knowledge_points_in_questions(questions_data)
    
    # 4. 测试几个具体的知识点
    test_knowledge_points = ['K3', 'K4', 'K13', 'K35', 'K87']
    
    print(f"\n🧪 测试具体知识点:")
    for kp_id in test_knowledge_points:
        test_specific_knowledge_point(kp_id, questions_data, knowledge_points_mapping)
    
    # 5. 检查映射关系
    print(f"\n🔍 检查映射关系:")
    mapped_kps = set(knowledge_points_mapping.keys())
    question_kps = all_knowledge_points
    
    print(f"   映射文件中的知识点: {len(mapped_kps)}")
    print(f"   题目中的知识点: {len(question_kps)}")
    
    # 找出在题目中但不在映射中的知识点
    missing_in_mapping = question_kps - mapped_kps
    if missing_in_mapping:
        print(f"   ❌ 在题目中但不在映射中的知识点: {list(missing_in_mapping)[:10]}")
    
    # 找出在映射中但不在题目中的知识点
    missing_in_questions = mapped_kps - question_kps
    if missing_in_questions:
        print(f"   ⚠️  在映射中但不在题目中的知识点: {list(missing_in_questions)[:10]}")
    
    print("\n" + "=" * 60)
    print("🎉 调试完成")

if __name__ == '__main__':
    main()
