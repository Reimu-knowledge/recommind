#!/usr/bin/env python3
"""
测试教师端知识点得分修正
验证教师端显示的知识点得分是否基于真实答题记录
"""

import requests
import json

# API基础URL
BASE_URL = 'http://localhost:5000'

def test_teacher_knowledge_scores():
    """测试教师端知识点得分"""
    print("🧪 测试教师端知识点得分修正")
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
    
    # 2. 获取所有学生列表
    print("\n2. 获取学生列表")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students")
        if response.status_code == 200:
            students_data = response.json()
            students = students_data.get('students', [])
            
            if not students:
                print("❌ 没有找到学生数据")
                return
            
            print(f"✅ 获取到 {len(students)} 个学生")
            
            # 选择第一个学生进行测试
            test_student = students[0]
            student_id = test_student['id']
            student_name = test_student['name']
            
            print(f"✅ 选择测试学生: {student_name} ({student_id})")
            
        else:
            print(f"❌ 获取学生列表失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取学生列表异常: {e}")
        return
    
    # 3. 获取学生详情，检查知识点得分
    print("\n3. 检查学生知识点得分")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students/{student_id}")
        if response.status_code == 200:
            result = response.json()
            student_detail = result.get('data', {})
            knowledge_scores = student_detail.get('knowledge_scores', [])
            
            print(f"✅ 获取学生详情成功，共 {len(knowledge_scores)} 个知识点")
            
            if knowledge_scores:
                print("\n📊 知识点得分详情:")
                for i, kp in enumerate(knowledge_scores, 1):
                    print(f"   {i}. {kp['knowledge_point_name']} ({kp['knowledge_point_id']})")
                    print(f"      得分: {kp['score']}%")
                    print(f"      答题次数: {kp['practice_count']}")
                    print(f"      正确次数: {kp['correct_count']}")
                    
                    # 验证得分计算
                    if kp['practice_count'] > 0:
                        expected_score = int((kp['correct_count'] / kp['practice_count']) * 100)
                        actual_score = kp['score']
                        
                        if expected_score == actual_score:
                            print(f"      ✅ 得分计算正确 ({actual_score}%)")
                        else:
                            print(f"      ❌ 得分计算错误 (期望: {expected_score}%, 实际: {actual_score}%)")
                    else:
                        print(f"      ⚠️ 无答题记录")
                    print()
                
                # 检查是否有薄弱知识点
                weak_points = [kp for kp in knowledge_scores if kp['score'] < 70]
                if weak_points:
                    print(f"🔍 发现 {len(weak_points)} 个薄弱知识点:")
                    for wp in weak_points:
                        print(f"   • {wp['knowledge_point_name']}: {wp['score']}%")
                else:
                    print("✅ 没有薄弱知识点")
                
            else:
                print("ℹ️ 该学生暂无知识点得分数据")
                
        else:
            print(f"❌ 获取学生详情失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取学生详情异常: {e}")
        return
    
    # 4. 获取知识点总体统计
    print("\n4. 检查知识点总体统计")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/knowledge-points/stats")
        if response.status_code == 200:
            result = response.json()
            kp_stats = result.get('knowledge_point_stats', [])
            
            print(f"✅ 获取知识点统计成功，共 {len(kp_stats)} 个知识点")
            
            if kp_stats:
                print("\n📈 知识点总体统计:")
                for i, kp in enumerate(kp_stats[:5], 1):  # 只显示前5个
                    print(f"   {i}. {kp['knowledge_point_name']} ({kp['knowledge_point_id']})")
                    print(f"      总体正确率: {kp['overall_accuracy']}%")
                    print(f"      平均掌握率: {kp['average_mastery']}%")
                    print(f"      掌握学生数: {kp['mastered_students']}")
                    print(f"      薄弱学生数: {kp['weak_students']}")
                    print(f"      掌握率: {kp['mastery_rate']}%")
                    print()
                
                # 检查排序
                print("📊 排序检查:")
                mastery_rates = [kp['average_mastery'] for kp in kp_stats]
                is_sorted = all(mastery_rates[i] >= mastery_rates[i+1] for i in range(len(mastery_rates)-1))
                
                if is_sorted:
                    print("   ✅ 知识点按平均掌握率从高到低正确排序")
                else:
                    print("   ❌ 知识点排序不正确")
                
            else:
                print("ℹ️ 暂无知识点统计数据")
                
        else:
            print(f"❌ 获取知识点统计失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取知识点统计异常: {e}")
        return
    
    # 5. 对比学生端和教师端数据一致性
    print("\n5. 对比数据一致性")
    try:
        # 获取学生端薄弱知识点
        response = requests.get(f"{BASE_URL}/api/students/{student_id}/weak-points?threshold=0.3")
        if response.status_code == 200:
            result = response.json()
            weak_points = result.get('weak_knowledge_points', [])
            
            print(f"✅ 获取学生端薄弱知识点: {len(weak_points)} 个")
            
            # 获取教师端知识点得分
            response = requests.get(f"{BASE_URL}/api/teacher/students/{student_id}")
            if response.status_code == 200:
                result = response.json()
                student_detail = result.get('data', {})
                knowledge_scores = student_detail.get('knowledge_scores', [])
                
                print(f"✅ 获取教师端知识点得分: {len(knowledge_scores)} 个")
                
                # 对比数据一致性
                print("\n🔍 数据一致性检查:")
                consistency_ok = True
                
                for wp in weak_points:
                    # 在学生端薄弱知识点中查找对应的教师端得分
                    teacher_kp = next((kp for kp in knowledge_scores if kp['knowledge_point_id'] == wp['id']), None)
                    
                    if teacher_kp:
                        student_accuracy = wp['accuracy']
                        teacher_score = teacher_kp['score']
                        
                        if abs(student_accuracy - teacher_score) < 1:  # 允许1%的误差
                            print(f"   ✅ {wp['name']}: 数据一致 (学生端: {student_accuracy}%, 教师端: {teacher_score}%)")
                        else:
                            print(f"   ❌ {wp['name']}: 数据不一致 (学生端: {student_accuracy}%, 教师端: {teacher_score}%)")
                            consistency_ok = False
                    else:
                        print(f"   ⚠️ {wp['name']}: 教师端无对应数据")
                
                if consistency_ok:
                    print("\n✅ 学生端和教师端数据一致性检查通过")
                else:
                    print("\n❌ 学生端和教师端数据存在不一致")
                
            else:
                print(f"❌ 获取教师端数据失败: {response.text}")
                return
        else:
            print(f"❌ 获取学生端数据失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 数据一致性检查异常: {e}")
        return
    
    print("\n🎉 教师端知识点得分测试完成！")
    print("=" * 50)

def main():
    """主函数"""
    test_teacher_knowledge_scores()

if __name__ == '__main__':
    main()
