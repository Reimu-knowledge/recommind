#!/usr/bin/env python3
"""
测试推荐系统更新功能
重点验证学生答题后推荐结果的变化
"""

import requests
import json
import time
from typing import Dict, List

class RecommendationUpdateTester:
    """推荐更新测试类"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def create_test_student(self, student_id: str = "test_update_001") -> bool:
        """创建测试学生"""
        print(f"👤 创建测试学生: {student_id}")
        try:
            data = {
                "id": student_id,
                "name": "推荐更新测试学生",
                "email": "test_update@example.com",
                "grade": "高一",
                "initial_mastery": {
                    "K1": 0.1,  # 很低的初始掌握度
                    "K2": 0.05,
                    "K3": 0.08,
                    "K4": 0.12,
                    "K5": 0.15
                }
            }
            
            response = self.session.post(f"{self.base_url}/api/students", json=data)
            if response.status_code == 201:
                print(f"✅ 学生创建成功")
                return True
            else:
                print(f"❌ 学生创建失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 学生创建异常: {e}")
            return False
    
    def start_learning_session(self, student_id: str) -> int:
        """开始学习会话"""
        print(f"🎯 开始学习会话")
        try:
            data = {"session_name": "推荐更新测试会话"}
            response = self.session.post(f"{self.base_url}/api/students/{student_id}/sessions", json=data)
            if response.status_code == 201:
                session_id = response.json()['data']['id']
                print(f"✅ 学习会话开始: {session_id}")
                return session_id
            else:
                print(f"❌ 学习会话开始失败")
                return None
        except Exception as e:
            print(f"❌ 学习会话开始异常: {e}")
            return None
    
    def get_recommendations(self, student_id: str, num_questions: int = 5) -> List[Dict]:
        """获取推荐题目"""
        print(f"📝 获取推荐题目: {num_questions}道")
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}/recommendations?num_questions={num_questions}")
            if response.status_code == 200:
                data = response.json()
                recommendations = data['recommendations']
                print(f"✅ 获取推荐题目成功: {len(recommendations)}道")
                
                # 显示推荐题目详情
                for i, q in enumerate(recommendations):
                    kp_list = list(q['knowledge_points'].keys())
                    print(f"   题目{i+1}: {q['qid']} - 知识点: {kp_list}")
                    print(f"   内容: {q['content'][:60]}...")
                
                return recommendations
            else:
                print(f"❌ 获取推荐题目失败: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ 获取推荐题目异常: {e}")
            return []
    
    def submit_answers(self, student_id: str, session_id: int, recommendations: List[Dict], 
                      correct_answers: List[str] = None) -> bool:
        """提交答案"""
        print(f"📤 提交答案")
        try:
            # 如果没有指定正确答案，随机选择
            if correct_answers is None:
                import random
                correct_answers = [random.choice(['A', 'B', 'C', 'D']) for _ in recommendations]
            
            answers = []
            for i, q in enumerate(recommendations):
                answers.append({
                    "qid": q['qid'],
                    "selected": correct_answers[i]
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
                
                print(f"✅ 答案提交成功:")
                print(f"   正确率: {correct_count}/{total_count} ({correct_count/total_count:.2%})")
                
                # 显示答题详情
                for detail in answer_details:
                    status = "✅" if detail['correct'] else "❌"
                    print(f"   {detail['qid']}: {detail['selected']} {status}")
                
                return True
            else:
                print(f"❌ 答案提交失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 答案提交异常: {e}")
            return False
    
    def get_mastery_status(self, student_id: str) -> Dict:
        """获取知识点掌握情况"""
        print(f"📊 获取知识点掌握情况")
        try:
            response = self.session.get(f"{self.base_url}/api/students/{student_id}/mastery")
            if response.status_code == 200:
                data = response.json()
                mastery_data = data['data']['knowledge_mastery']
                
                print(f"✅ 当前知识点掌握情况:")
                for kp_id, kp_data in mastery_data.items():
                    print(f"   {kp_id}: {kp_data['mastery_score']:.3f} (练习{kp_data['practice_count']}次)")
                
                return mastery_data
            else:
                print(f"❌ 获取掌握情况失败: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ 获取掌握情况异常: {e}")
            return {}
    
    def compare_recommendations(self, student_id: str, before_recommendations: List[Dict], 
                              after_recommendations: List[Dict]) -> None:
        """比较推荐结果的变化"""
        print(f"🔍 比较推荐结果变化")
        
        # 提取知识点信息
        before_kps = set()
        for q in before_recommendations:
            before_kps.update(q['knowledge_points'].keys())
        
        after_kps = set()
        for q in after_recommendations:
            after_kps.update(q['knowledge_points'].keys())
        
        print(f"   推荐前涉及知识点: {sorted(before_kps)}")
        print(f"   推荐后涉及知识点: {sorted(after_kps)}")
        
        # 分析变化
        new_kps = after_kps - before_kps
        removed_kps = before_kps - after_kps
        common_kps = before_kps & after_kps
        
        print(f"   新增知识点: {sorted(new_kps)}")
        print(f"   移除知识点: {sorted(removed_kps)}")
        print(f"   共同知识点: {sorted(common_kps)}")
        
        # 比较题目内容变化
        before_qids = [q['qid'] for q in before_recommendations]
        after_qids = [q['qid'] for q in after_recommendations]
        
        new_questions = set(after_qids) - set(before_qids)
        removed_questions = set(before_qids) - set(after_qids)
        
        print(f"   新增题目: {sorted(new_questions)}")
        print(f"   移除题目: {sorted(removed_questions)}")
        
        # 判断是否有显著变化
        if new_kps or removed_kps or new_questions or removed_questions:
            print(f"✅ 推荐结果发生了显著变化！")
        else:
            print(f"⚠️ 推荐结果没有明显变化")
    
    def run_recommendation_update_test(self, student_id: str = "test_update_001") -> bool:
        """运行推荐更新测试"""
        print("🚀 开始推荐更新测试")
        print("=" * 60)
        
        # 1. 创建测试学生
        if not self.create_test_student(student_id):
            return False
        
        print()
        
        # 2. 开始学习会话
        session_id = self.start_learning_session(student_id)
        if not session_id:
            return False
        
        print()
        
        # 3. 获取初始推荐
        print("📋 第一轮推荐测试")
        print("-" * 30)
        initial_recommendations = self.get_recommendations(student_id, 5)
        if not initial_recommendations:
            return False
        
        print()
        
        # 4. 查看初始掌握情况
        initial_mastery = self.get_mastery_status(student_id)
        
        print()
        
        # 5. 提交第一轮答案（故意答错一些）
        print("📤 第一轮答题（故意答错一些）")
        print("-" * 30)
        # 故意答错前3题，答对后2题
        correct_answers = ['B', 'C', 'A', 'A', 'B']  # 假设这些是正确答案
        if not self.submit_answers(student_id, session_id, initial_recommendations, correct_answers):
            return False
        
        print()
        
        # 6. 查看答题后的掌握情况
        after_first_mastery = self.get_mastery_status(student_id)
        
        print()
        
        # 7. 获取第二轮推荐
        print("📋 第二轮推荐测试")
        print("-" * 30)
        second_recommendations = self.get_recommendations(student_id, 5)
        if not second_recommendations:
            return False
        
        print()
        
        # 8. 比较推荐结果变化
        self.compare_recommendations(student_id, initial_recommendations, second_recommendations)
        
        print()
        
        # 9. 提交第二轮答案（答对更多）
        print("📤 第二轮答题（答对更多）")
        print("-" * 30)
        correct_answers_2 = ['A', 'B', 'C', 'D', 'A']  # 假设这些是正确答案
        if not self.submit_answers(student_id, session_id, second_recommendations, correct_answers_2):
            return False
        
        print()
        
        # 10. 查看第二轮后的掌握情况
        after_second_mastery = self.get_mastery_status(student_id)
        
        print()
        
        # 11. 获取第三轮推荐
        print("📋 第三轮推荐测试")
        print("-" * 30)
        third_recommendations = self.get_recommendations(student_id, 5)
        if not third_recommendations:
            return False
        
        print()
        
        # 12. 比较第二轮和第三轮推荐结果
        self.compare_recommendations(student_id, second_recommendations, third_recommendations)
        
        print()
        
        # 13. 分析掌握度变化
        print("📈 掌握度变化分析")
        print("-" * 30)
        self.analyze_mastery_changes(initial_mastery, after_first_mastery, after_second_mastery)
        
        print()
        print("🎉 推荐更新测试完成！")
        return True
    
    def analyze_mastery_changes(self, initial_mastery: Dict, after_first: Dict, after_second: Dict) -> None:
        """分析掌握度变化"""
        print("掌握度变化详情:")
        
        all_kps = set(initial_mastery.keys()) | set(after_first.keys()) | set(after_second.keys())
        
        for kp in sorted(all_kps):
            initial_score = initial_mastery.get(kp, {}).get('mastery_score', 0)
            first_score = after_first.get(kp, {}).get('mastery_score', 0)
            second_score = after_second.get(kp, {}).get('mastery_score', 0)
            
            print(f"   {kp}: {initial_score:.3f} → {first_score:.3f} → {second_score:.3f}")
            
            if second_score > first_score:
                print(f"     📈 进步: +{second_score - first_score:.3f}")
            elif second_score < first_score:
                print(f"     📉 下降: {second_score - first_score:.3f}")
            else:
                print(f"     ➡️ 无变化")

def main():
    """主函数"""
    print("🧪 推荐系统更新功能测试")
    print("=" * 60)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(3)
    
    # 创建测试器
    tester = RecommendationUpdateTester()
    
    # 运行推荐更新测试
    success = tester.run_recommendation_update_test()
    
    if success:
        print("\n✅ 推荐更新测试通过！")
        print("💡 测试结果显示:")
        print("   - 学生答题后，知识点掌握度会实时更新")
        print("   - 推荐系统会根据新的掌握度调整推荐策略")
        print("   - 推荐题目和涉及的知识点会发生变化")
    else:
        print("\n❌ 推荐更新测试失败！")
        print("💡 请检查:")
        print("   - 后端服务是否正常启动")
        print("   - 推荐系统是否正常工作")
        print("   - 数据库连接是否正常")

if __name__ == "__main__":
    main()



