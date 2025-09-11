#!/usr/bin/env python3
"""
测试薄弱知识点更新
验证学生提交答案后，薄弱知识点是否正确更新
"""

import requests
import json
import time

# API基础URL
BASE_URL = 'http://localhost:5000'

def test_weak_points_update():
    """测试薄弱知识点更新"""
    print("🧪 测试薄弱知识点更新")
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
    
    # 2. 获取测试学生
    print("\n2. 获取测试学生")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students")
        if response.status_code == 200:
            result = response.json()
            students = result.get('students', [])
            
            if not students:
                print("❌ 没有找到学生数据")
                return
            
            # 选择第一个有答题记录的学生
            test_student = None
            for student in students:
                if student.get('total_questions', 0) > 0:
                    test_student = student
                    break
            
            if not test_student:
                print("❌ 没有找到有答题记录的学生")
                return
            
            student_id = test_student['id']
            student_name = test_student['name']
            print(f"✅ 选择测试学生: {student_name} ({student_id})")
            print(f"   当前完成题目: {test_student.get('total_questions', 0)}")
            print(f"   当前正确率: {test_student.get('correct_rate', 0)}%")
            
        else:
            print(f"❌ 获取学生列表失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取学生列表异常: {e}")
        return
    
    # 3. 获取当前薄弱知识点
    print(f"\n3. 获取学生 {student_name} 当前薄弱知识点")
    try:
        response = requests.get(f"{BASE_URL}/api/students/{student_id}/weak-points")
        if response.status_code == 200:
            result = response.json()
            weak_points = result.get('weak_knowledge_points', [])
            
            print(f"✅ 当前薄弱知识点数量: {len(weak_points)}")
            
            if weak_points:
                print("\n📊 当前薄弱知识点详情:")
                for i, wp in enumerate(weak_points[:5], 1):  # 只显示前5个
                    print(f"   {i}. {wp.get('name', 'N/A')} ({wp.get('id', 'N/A')})")
                    print(f"      答题次数: {wp.get('total_attempts', 0)}")
                    print(f"      正确次数: {wp.get('correct_attempts', 0)}")
                    print(f"      正确率: {wp.get('accuracy', 0)}%")
                    print()
            else:
                print("ℹ️ 当前没有薄弱知识点")
                
        else:
            print(f"❌ 获取薄弱知识点失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取薄弱知识点异常: {e}")
        return
    
    # 4. 开始学习会话
    print(f"\n4. 开始学习会话")
    try:
        response = requests.post(
            f"{BASE_URL}/api/students/{student_id}/sessions",
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code == 200:
            result = response.json()
            session_id = result.get('session_id')
            print(f"✅ 学习会话开始成功，会话ID: {session_id}")
        else:
            print(f"❌ 开始学习会话失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 开始学习会话异常: {e}")
        return
    
    # 5. 获取推荐题目
    print(f"\n5. 获取推荐题目")
    try:
        response = requests.get(f"{BASE_URL}/api/students/{student_id}/recommendations")
        if response.status_code == 200:
            result = response.json()
            questions = result.get('questions', [])
            
            print(f"✅ 获取到 {len(questions)} 道推荐题目")
            
            if questions:
                # 选择第一道题目进行测试
                test_question = questions[0]
                question_id = test_question['qid']
                question_content = test_question['content'][:50] + "..."
                
                print(f"✅ 选择测试题目: {question_id}")
                print(f"   题目内容: {question_content}")
                
                # 获取题目选项
                options = test_question.get('options', {})
                print(f"   选项: {list(options.keys())}")
                
                # 获取正确答案
                correct_answer = test_question.get('answer', '')
                print(f"   正确答案: {correct_answer}")
                
            else:
                print("❌ 没有推荐题目")
                return
                
        else:
            print(f"❌ 获取推荐题目失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 获取推荐题目异常: {e}")
        return
    
    # 6. 提交答案（故意答错）
    print(f"\n6. 提交答案测试")
    try:
        # 构造答案数据
        answers = [{
            'qid': question_id,
            'selected': 'A',  # 故意选择错误答案
            'timestamp': int(time.time())
        }]
        
        submit_data = {
            'answers': answers,
            'session_id': session_id
        }
        
        print(f"   提交答案: {answers[0]['selected']} (正确答案: {correct_answer})")
        
        response = requests.post(
            f"{BASE_URL}/api/students/{student_id}/answers",
            json=submit_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 答案提交成功")
            
            # 检查答题结果
            answer_details = result.get('answer_details', [])
            if answer_details:
                detail = answer_details[0]
                print(f"   答题结果: {'正确' if detail.get('correct') else '错误'}")
                print(f"   涉及知识点: {detail.get('knowledge_points', [])}")
            
        else:
            print(f"❌ 答案提交失败: {response.text}")
            return
            
    except Exception as e:
        print(f"❌ 答案提交异常: {e}")
        return
    
    # 7. 等待一下，然后重新获取薄弱知识点
    print(f"\n7. 等待2秒后重新获取薄弱知识点")
    time.sleep(2)
    
    try:
        response = requests.get(f"{BASE_URL}/api/students/{student_id}/weak-points")
        if response.status_code == 200:
            result = response.json()
            new_weak_points = result.get('weak_knowledge_points', [])
            
            print(f"✅ 更新后薄弱知识点数量: {len(new_weak_points)}")
            
            if new_weak_points:
                print("\n📊 更新后薄弱知识点详情:")
                for i, wp in enumerate(new_weak_points[:5], 1):  # 只显示前5个
                    print(f"   {i}. {wp.get('name', 'N/A')} ({wp.get('id', 'N/A')})")
                    print(f"      答题次数: {wp.get('total_attempts', 0)}")
                    print(f"      正确次数: {wp.get('correct_attempts', 0)}")
                    print(f"      正确率: {wp.get('accuracy', 0)}%")
                    print()
            else:
                print("ℹ️ 更新后没有薄弱知识点")
                
        else:
            print(f"❌ 重新获取薄弱知识点失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 重新获取薄弱知识点异常: {e}")
        return
    
    # 8. 比较更新前后的变化
    print(f"\n8. 比较更新前后的变化")
    
    # 统计变化
    old_count = len(weak_points) if 'weak_points' in locals() else 0
    new_count = len(new_weak_points) if 'new_weak_points' in locals() else 0
    
    print(f"   薄弱知识点数量变化: {old_count} → {new_count}")
    
    if old_count != new_count:
        print("✅ 薄弱知识点数量发生变化")
    else:
        print("ℹ️ 薄弱知识点数量未变化")
    
    # 检查具体知识点的变化
    old_kp_ids = {wp.get('id') for wp in weak_points} if 'weak_points' in locals() else set()
    new_kp_ids = {wp.get('id') for wp in new_weak_points} if 'new_weak_points' in locals() else set()
    
    added_kps = new_kp_ids - old_kp_ids
    removed_kps = old_kp_ids - new_kp_ids
    
    if added_kps:
        print(f"   新增薄弱知识点: {list(added_kps)}")
    if removed_kps:
        print(f"   移除薄弱知识点: {list(removed_kps)}")
    
    # 9. 检查数据库中的答题记录
    print(f"\n9. 检查数据库答题记录")
    try:
        response = requests.get(f"{BASE_URL}/api/teacher/students/{student_id}")
        if response.status_code == 200:
            result = response.json()
            student_data = result.get('student', {})
            
            print(f"   学生总答题数: {student_data.get('total_questions', 0)}")
            print(f"   学生总正确数: {student_data.get('correct_answers', 0)}")
            print(f"   学生总正确率: {student_data.get('correct_rate', 0)}%")
            
            # 检查知识点得分
            knowledge_scores = student_data.get('knowledge_scores', [])
            print(f"   知识点得分数量: {len(knowledge_scores)}")
            
            if knowledge_scores:
                print("   知识点得分详情:")
                for kp in knowledge_scores[:3]:  # 只显示前3个
                    print(f"     {kp.get('knowledge_point_name', 'N/A')}: {kp.get('score', 0)}%")
            
        else:
            print(f"❌ 获取学生详情失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 获取学生详情异常: {e}")
    
    print("\n🎉 薄弱知识点更新测试完成！")
    print("=" * 50)

def main():
    """主函数"""
    test_weak_points_update()

if __name__ == '__main__':
    main()
