#!/usr/bin/env python3
"""
API测试脚本
用于测试教育推荐系统后端API的功能
"""

import requests
import json
import time
from typing import Dict, List

class APITester:
    """API测试类"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def test_health_check(self) -> bool:
        """测试健康检查接口"""
        print("🔍 测试健康检查接口...")
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查成功: {data['message']}")
                print(f"   推荐系统状态: {data['recommendation_system']}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False
    
    def test_create_student(self, student_id: str = "test_student_001") -> bool:
        """测试创建学生"""
        print(f"👤 测试创建学生: {student_id}")
        try:
            data = {
                "id": student_id,
                "name": "测试学生",
                "email": "test@example.com",
                "grade": "高一",
                "initial_mastery": {
                    "K1": 0.2,
                    "K2": 0.1,
                    "K3": 0.15
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/students", json=data)
            if response.status_code == 201:
                result = response.json()
                print(f"✅ 学生创建成功: {result['message']}")
                return True
            else:
                print(f"❌ 学生创建失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 学生创建异常: {e}")
            return False
    
    def test_get_student(self, student_id: str = "test_student_001") -> bool:
        """测试获取学生信息"""
        print(f"📋 测试获取学生信息: {student_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}")
            if response.status_code == 200:
                data = response.json()
                student_data = data['data']
                print(f"✅ 获取学生信息成功:")
                print(f"   姓名: {student_data['name']}")
                print(f"   年级: {student_data['grade']}")
                print(f"   总题目数: {student_data['total_questions']}")
                print(f"   准确率: {student_data['overall_accuracy']:.2%}")
                return True
            else:
                print(f"❌ 获取学生信息失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取学生信息异常: {e}")
            return False
    
    def test_start_session(self, student_id: str = "test_student_001") -> int:
        """测试开始学习会话"""
        print(f"🎯 测试开始学习会话: {student_id}")
        try:
            data = {
                "session_name": "API测试会话"
            }
            
            response = self.session.post(f"{self.base_url}/api/students/{student_id}/sessions", json=data)
            if response.status_code == 201:
                result = response.json()
                session_data = result['data']
                session_id = session_data['id']
                print(f"✅ 学习会话开始成功: {session_id}")
                return session_id
            else:
                print(f"❌ 学习会话开始失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return None
        except Exception as e:
            print(f"❌ 学习会话开始异常: {e}")
            return None
    
    def test_get_recommendations(self, student_id: str = "test_student_001", num_questions: int = 3) -> List[Dict]:
        """测试获取推荐题目"""
        print(f"📝 测试获取推荐题目: {num_questions}道")
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}/recommendations?num_questions={num_questions}")
            if response.status_code == 200:
                data = response.json()
                recommendations = data['recommendations']
                print(f"✅ 获取推荐题目成功: {len(recommendations)}道")
                
                for i, q in enumerate(recommendations):
                    print(f"   题目{i+1}: {q['qid']} - {q['content'][:50]}...")
                    print(f"   选项: {q['options']}")
                    print(f"   知识点: {list(q['knowledge_points'].keys())}")
                
                return recommendations
            else:
                print(f"❌ 获取推荐题目失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return []
        except Exception as e:
            print(f"❌ 获取推荐题目异常: {e}")
            return []
    
    def test_submit_answers(self, student_id: str, session_id: int, recommendations: List[Dict]) -> bool:
        """测试提交答案"""
        print(f"📤 测试提交答案: {len(recommendations)}道题")
        try:
            # 模拟答题（随机选择答案）
            import random
            answers = []
            for q in recommendations:
                selected = random.choice(['A', 'B', 'C', 'D'])
                answers.append({
                    "qid": q['qid'],
                    "selected": selected
                })
            
            data = {
                "session_id": session_id,
                "answers": answers
            }
            
            response = self.session.post(f"{self.base_url}/api/students/{student_id}/answers", json=data)
            if response.status_code == 200:
                result = response.json()
                answer_details = result['answer_details']
                correct_count = sum(1 for detail in answer_details if detail['correct'])
                total_count = len(answer_details)
                accuracy = correct_count / total_count if total_count > 0 else 0
                
                print(f"✅ 答案提交成功:")
                print(f"   正确率: {correct_count}/{total_count} ({accuracy:.2%})")
                print(f"   当前掌握知识点: {result['mastered_knowledge_points']}")
                
                # 显示答题详情
                for detail in answer_details:
                    status = "✅" if detail['correct'] else "❌"
                    print(f"   {detail['qid']}: {detail['selected']} {status}")
                
                return True
            else:
                print(f"❌ 答案提交失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 答案提交异常: {e}")
            return False
    
    def test_get_mastery(self, student_id: str = "test_student_001") -> bool:
        """测试获取知识点掌握情况"""
        print(f"📊 测试获取知识点掌握情况: {student_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}/mastery")
            if response.status_code == 200:
                data = response.json()
                mastery_data = data['data']
                print(f"✅ 获取知识点掌握情况成功:")
                print(f"   总知识点数: {mastery_data['total_knowledge_points']}")
                print(f"   已掌握: {mastery_data['mastered_points']}")
                
                # 显示前5个知识点的掌握情况
                mastery_scores = mastery_data['knowledge_mastery']
                for i, (kp_id, kp_data) in enumerate(list(mastery_scores.items())[:5]):
                    print(f"   {kp_id}: {kp_data['mastery_score']:.3f} (练习{kp_data['practice_count']}次)")
                
                return True
            else:
                print(f"❌ 获取知识点掌握情况失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取知识点掌握情况异常: {e}")
            return False
    
    def test_get_weak_points(self, student_id: str = "test_student_001") -> bool:
        """测试获取薄弱知识点分析"""
        print(f"🔍 测试获取薄弱知识点分析: {student_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}/weak-points?threshold=0.3")
            if response.status_code == 200:
                data = response.json()
                weak_points = data['weak_knowledge_points']
                recommendations = data['recommendations']
                
                print(f"✅ 获取薄弱知识点分析成功:")
                print(f"   薄弱知识点数量: {len(weak_points)}")
                
                if weak_points:
                    print("   薄弱知识点详情:")
                    for kp, score in weak_points[:3]:  # 显示前3个
                        print(f"     {kp}: {score:.3f}")
                
                print("   学习建议:")
                for rec in recommendations[:3]:  # 显示前3个建议
                    print(f"     {rec}")
                
                return True
            else:
                print(f"❌ 获取薄弱知识点分析失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取薄弱知识点分析异常: {e}")
            return False
    
    def test_end_session(self, session_id: int) -> bool:
        """测试结束学习会话"""
        print(f"🏁 测试结束学习会话: {session_id}")
        try:
            response = self.session.put(f"{self.base_url}/api/sessions/{session_id}")
            if response.status_code == 200:
                result = response.json()
                session_data = result['data']
                print(f"✅ 学习会话结束成功:")
                print(f"   总题目数: {session_data['total_questions']}")
                print(f"   正确答案数: {session_data['correct_answers']}")
                print(f"   准确率: {session_data['accuracy']:.2%}")
                return True
            else:
                print(f"❌ 学习会话结束失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 学习会话结束异常: {e}")
            return False
    
    def run_full_test(self, student_id: str = "test_student_001") -> bool:
        """运行完整测试流程"""
        print("🚀 开始完整API测试流程")
        print("=" * 60)
        
        # 1. 健康检查
        if not self.test_health_check():
            return False
        
        print()
        
        # 2. 创建学生
        if not self.test_create_student(student_id):
            return False
        
        print()
        
        # 3. 获取学生信息
        if not self.test_get_student(student_id):
            return False
        
        print()
        
        # 4. 开始学习会话
        session_id = self.test_start_session(student_id)
        if not session_id:
            return False
        
        print()
        
        # 5. 获取推荐题目
        recommendations = self.test_get_recommendations(student_id, 3)
        if not recommendations:
            return False
        
        print()
        
        # 6. 提交答案
        if not self.test_submit_answers(student_id, session_id, recommendations):
            return False
        
        print()
        
        # 7. 获取知识点掌握情况
        if not self.test_get_mastery(student_id):
            return False
        
        print()
        
        # 8. 获取薄弱知识点分析
        if not self.test_get_weak_points(student_id):
            return False
        
        print()
        
        # 9. 结束学习会话
        if not self.test_end_session(session_id):
            return False
        
        print()
        print("🎉 完整测试流程完成！")
        return True

def main():
    """主函数"""
    print("🧪 教育推荐系统API测试工具")
    print("=" * 60)
    
    # 创建测试器
    tester = APITester()
    
    # 运行完整测试
    success = tester.run_full_test()
    
    if success:
        print("\n✅ 所有测试通过！API服务运行正常。")
    else:
        print("\n❌ 测试失败！请检查API服务状态。")
    
    print("\n💡 提示:")
    print("   - 确保后端服务已启动: python app_simple.py")
    print("   - 确保推荐系统可正常运行")
    print("   - 检查端口5000是否被占用")

if __name__ == "__main__":
    main()

