#!/usr/bin/env python3
"""
测试薄弱知识点计算逻辑
验证基于真实答题记录的正确率计算是否正确
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:5000'

def test_weak_points_calculation():
    """测试薄弱知识点计算"""
    print("🧪 测试薄弱知识点计算逻辑")
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
    
    # 2. 创建测试学生
    print("\n2. 创建测试学生")
    test_student_id = "weak_points_test_001"
    student_data = {
        "id": test_student_id,
        "name": "薄弱知识点测试学生",
        "email": "test@example.com",
        "grade": "测试班级"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/students", json=student_data)
        if response.status_code == 201:
            print("✅ 测试学生创建成功")
        else:
            print(f"❌ 创建学生失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 创建学生异常: {e}")
        return
    
    # 3. 开始学习会话
    print("\n3. 开始学习会话")
    session_data = {"session_name": "薄弱知识点测试会话"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/students/{test_student_id}/sessions", json=session_data)
        if response.status_code == 201:
            session_info = response.json()
            session_id = session_info['data']['id']
            print(f"✅ 学习会话开始成功，会话ID: {session_id}")
        else:
            print(f"❌ 开始会话失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 开始会话异常: {e}")
        return
    
    # 4. 提交一些答案（模拟学习过程）
    print("\n4. 提交测试答案")
    
    # 模拟一些答题情况：故意答错一些题目来测试薄弱知识点
    test_answers = [
        {"qid": "Q1", "selected": "A"},  # 假设Q1正确答案是B，这里答错
        {"qid": "Q2", "selected": "B"},  # 假设Q2正确答案是B，这里答对
        {"qid": "Q3", "selected": "C"},  # 假设Q3正确答案是D，这里答错
        {"qid": "Q4", "selected": "A"},  # 假设Q4正确答案是A，这里答对
        {"qid": "Q5", "selected": "B"},  # 假设Q5正确答案是C，这里答错
    ]
    
    answers_data = {
        "answers": test_answers,
        "session_id": session_id
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/students/{test_student_id}/answers", json=answers_data)
        if response.status_code == 200:
            result = response.json()
            print("✅ 答案提交成功")
            print(f"📊 答题结果: {len(result['answer_details'])} 道题")
            
            # 显示答题详情
            for detail in result['answer_details']:
                status = "✅" if detail['correct'] else "❌"
                print(f"   {status} {detail['qid']}: 选择{detail['selected']}, 正确答案{detail['correct_answer']}")
        else:
            print(f"❌ 提交答案失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 提交答案异常: {e}")
        return
    
    # 5. 测试薄弱知识点分析
    print("\n5. 测试薄弱知识点分析")
    
    try:
        # 使用较低的阈值来更容易发现薄弱点
        response = requests.get(f"{BASE_URL}/api/students/{test_student_id}/weak-points?threshold=0.5")
        if response.status_code == 200:
            result = response.json()
            print("✅ 薄弱知识点分析成功")
            
            weak_points = result.get('weak_knowledge_points', [])
            print(f"📊 发现 {len(weak_points)} 个薄弱知识点:")
            
            for wp in weak_points:
                print(f"   🔴 {wp['name']} ({wp['id']})")
                print(f"      正确率: {wp['accuracy']}% ({wp['correct_attempts']}/{wp['total_attempts']})")
                print(f"      错误次数: {wp['wrong_attempts']}")
            
            # 显示总体统计
            overall_stats = result.get('overall_stats', {})
            print(f"\n📈 总体统计:")
            print(f"   总题目数: {overall_stats.get('total_questions', 0)}")
            print(f"   正确题目数: {overall_stats.get('total_correct', 0)}")
            print(f"   总体正确率: {overall_stats.get('overall_accuracy', 0)}%")
            
        else:
            print(f"❌ 薄弱知识点分析失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 薄弱知识点分析异常: {e}")
        return
    
    # 6. 测试教师端知识点统计
    print("\n6. 测试教师端知识点统计")
    
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/knowledge-points/stats")
        if response.status_code == 200:
            result = response.json()
            print("✅ 知识点统计获取成功")
            
            kp_stats = result.get('knowledge_point_stats', [])
            print(f"📊 知识点统计 (共{len(kp_stats)}个知识点):")
            
            for kp in kp_stats[:5]:  # 只显示前5个
                print(f"   📚 {kp['knowledge_point_name']} ({kp['knowledge_point_id']})")
                print(f"      总学生数: {kp['total_students']}")
                print(f"      总答题数: {kp['total_attempts']}")
                print(f"      正确答题数: {kp['correct_attempts']}")
                print(f"      总体正确率: {kp['overall_accuracy']}%")
                print(f"      平均掌握率: {kp['average_mastery']}%")
                print(f"      掌握学生数: {kp['mastered_students']}")
                print(f"      薄弱学生数: {kp['weak_students']}")
                print()
            
        else:
            print(f"❌ 知识点统计获取失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 知识点统计获取异常: {e}")
        return
    
    # 7. 清理测试数据（可选）
    print("\n7. 测试完成")
    print("ℹ️ 测试数据保留在数据库中，可以手动清理")
    
    print("\n🎉 薄弱知识点计算测试完成！")
    print("=" * 50)

def main():
    """主函数"""
    test_weak_points_calculation()

if __name__ == '__main__':
    main()
