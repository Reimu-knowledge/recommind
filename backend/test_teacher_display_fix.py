#!/usr/bin/env python3
"""
测试教师端知识点得分显示修正
验证教师端表格中知识点得分是否正确显示
"""

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:5000'

def test_teacher_display_fix():
    """测试教师端知识点得分显示"""
    print("🧪 测试教师端知识点得分显示修正")
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
    
    # 2. 获取学生列表数据
    print("\n2. 获取学生列表数据")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students")
        if response.status_code == 200:
            result = response.json()
            students = result.get('students', [])
            
            if not students:
                print("❌ 没有找到学生数据")
                return
            
            print(f"✅ 获取到 {len(students)} 个学生")
            
            # 检查第一个学生的数据结构
            test_student = students[0]
            student_id = test_student['id']
            student_name = test_student['name']
            
            print(f"✅ 测试学生: {student_name} ({student_id})")
            
            # 检查数据结构
            print("\n📊 学生数据结构检查:")
            print(f"   学号: {test_student.get('id', 'N/A')}")
            print(f"   姓名: {test_student.get('name', 'N/A')}")
            print(f"   班级: {test_student.get('grade', 'N/A')}")
            print(f"   完成题目: {test_student.get('total_questions', 0)}")
            print(f"   正确率: {test_student.get('correct_rate', 0)}%")
            
            # 检查知识点得分数据
            knowledge_scores = test_student.get('knowledge_scores', [])
            print(f"   知识点数量: {len(knowledge_scores)}")
            
            if knowledge_scores:
                print("\n📈 知识点得分详情:")
                for i, kp in enumerate(knowledge_scores, 1):
                    print(f"   {i}. {kp.get('knowledge_point_name', 'N/A')} ({kp.get('knowledge_point_id', 'N/A')})")
                    print(f"      得分: {kp.get('score', 0)}%")
                    print(f"      答题次数: {kp.get('practice_count', 0)}")
                    print(f"      正确次数: {kp.get('correct_count', 0)}")
                    print()
                
                # 检查前端显示所需的数据结构
                print("🔍 前端显示数据结构检查:")
                lowest_scores = sorted(knowledge_scores, key=lambda x: x.get('score', 0))[:2]
                
                print("   最低分知识点（前2个）:")
                for i, kp in enumerate(lowest_scores, 1):
                    kp_name = kp.get('knowledge_point_name', 'N/A')
                    kp_score = kp.get('score', 0)
                    print(f"   {i}. {kp_name}: {kp_score}%")
                
                # 验证前端模板所需字段
                print("\n✅ 前端模板字段验证:")
                for kp in lowest_scores:
                    required_fields = ['knowledge_point_name', 'score']
                    missing_fields = [field for field in required_fields if field not in kp]
                    
                    if not missing_fields:
                        print(f"   ✅ {kp.get('knowledge_point_name')}: 所有必需字段存在")
                    else:
                        print(f"   ❌ {kp.get('knowledge_point_name')}: 缺少字段 {missing_fields}")
                
            else:
                print("ℹ️ 该学生暂无知识点得分数据")
                
        else:
            print(f"❌ 获取学生列表失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取学生列表异常: {e}")
        return
    
    # 3. 模拟前端数据处理
    print("\n3. 模拟前端数据处理")
    try:
        # 模拟前端的数据映射逻辑
        students_data = students
        
        processed_students = []
        for student in students_data:
            processed_student = {
                'id': student.get('id'),
                'name': student.get('name'),
                'class': student.get('grade', '未知班级'),
                'knowledge_scores': student.get('knowledge_scores', []),
                'total_questions': student.get('total_questions', 0),
                'correct_rate': student.get('correct_rate', 0),
                'last_active': student.get('last_active', 'N/A')
            }
            processed_students.append(processed_student)
        
        print(f"✅ 处理了 {len(processed_students)} 个学生数据")
        
        # 检查处理后的数据结构
        test_processed = processed_students[0]
        print(f"\n📊 处理后数据结构:")
        print(f"   学号: {test_processed['id']}")
        print(f"   姓名: {test_processed['name']}")
        print(f"   班级: {test_processed['class']}")
        print(f"   知识点数量: {len(test_processed['knowledge_scores'])}")
        
        # 模拟getLowestScores函数
        def get_lowest_scores(knowledge_scores):
            if not knowledge_scores or len(knowledge_scores) == 0:
                return []
            
            # 按分数从低到高排序，取前两个
            return sorted(knowledge_scores, key=lambda x: x.get('score', 0))[:2]
        
        lowest_scores = get_lowest_scores(test_processed['knowledge_scores'])
        print(f"\n📈 最低分知识点（前2个）:")
        for i, kp in enumerate(lowest_scores, 1):
            kp_name = kp.get('knowledge_point_name', 'N/A')
            kp_score = kp.get('score', 0)
            print(f"   {i}. {kp_name}: {kp_score}%")
        
        # 模拟前端显示
        print(f"\n🖥️ 前端显示模拟:")
        print("   知识点得分列显示:")
        for i, kp in enumerate(lowest_scores, 1):
            kp_name = kp.get('knowledge_point_name', 'N/A')
            kp_score = kp.get('score', 0)
            weak_class = "weak" if kp_score < 70 else ""
            print(f"   {i}. <span class='score-tag {weak_class}'>{kp_name} {kp_score}%</span>")
        
        if len(test_processed['knowledge_scores']) > 2:
            more_count = len(test_processed['knowledge_scores']) - 2
            print(f"   +{more_count}项")
        
    except Exception as e:
        print(f"❌ 前端数据处理异常: {e}")
        return
    
    # 4. 检查数据一致性
    print("\n4. 检查数据一致性")
    try:
        # 检查是否有学生有知识点得分数据
        students_with_scores = [s for s in processed_students if s['knowledge_scores']]
        students_without_scores = [s for s in processed_students if not s['knowledge_scores']]
        
        print(f"✅ 有知识点得分的学生: {len(students_with_scores)} 个")
        print(f"ℹ️ 无知识点得分的学生: {len(students_without_scores)} 个")
        
        if students_with_scores:
            print("\n📊 有得分学生的统计:")
            for student in students_with_scores[:3]:  # 只显示前3个
                print(f"   {student['name']} ({student['id']}): {len(student['knowledge_scores'])} 个知识点")
                
                # 显示最低分知识点
                lowest = get_lowest_scores(student['knowledge_scores'])
                if lowest:
                    lowest_kp = lowest[0]
                    print(f"      最低分: {lowest_kp.get('knowledge_point_name')} {lowest_kp.get('score')}%")
        
        if students_without_scores:
            print("\n⚠️ 无得分学生列表:")
            for student in students_without_scores[:3]:  # 只显示前3个
                print(f"   {student['name']} ({student['id']})")
        
    except Exception as e:
        print(f"❌ 数据一致性检查异常: {e}")
        return
    
    print("\n🎉 教师端知识点得分显示测试完成！")
    print("=" * 50)

def main():
    """主函数"""
    test_teacher_display_fix()

if __name__ == '__main__':
    main()


