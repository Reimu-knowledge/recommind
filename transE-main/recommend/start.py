#!/usr/bin/env python3
"""
知识图谱推荐系统启动文件
提供命令行界面和API接口，用于前端集成
"""

import json
import os
import sys
import time
from typing import Dict, List, Optional
from simple_system import KnowledgeGraphRecommendationEngine

class EducationRecommendationAPI:
    """教育推荐系统API"""
    
    def __init__(self):
        """初始化推荐系统"""
        print("🚀 正在初始化知识图谱推荐系统...")
        try:
            self.engine = KnowledgeGraphRecommendationEngine(config_path='config.json')
            print("✅ 推荐系统初始化成功！")
        except Exception as e:
            print(f"❌ 推荐系统初始化失败: {e}")
            sys.exit(1)
        
        self.current_session = None
    
    def start_session(self, student_id: str, initial_mastery: Optional[Dict[str, float]] = None) -> Dict:
        """开始学习会话"""
        print(f"\n👨‍🎓 开始学生 {student_id} 的学习会话...")
        
        result = self.engine.create_student(student_id, initial_mastery)
        if result["status"] == "success":
            self.current_session = student_id
            print(f"✅ 学习会话开始成功！")
            print(f"📊 初始知识点掌握度:")
            for kp, score in result["initial_mastery"].items():
                print(f"   {kp}: {score:.2f}")
        else:
            print(f"❌ 学习会话开始失败: {result['message']}")
        
        return result
    
    def get_questions(self, num_questions: int = 3) -> Dict:
        """获取推荐题目"""
        if not self.current_session:
            return {
                "status": "error", 
                "message": "没有活跃的学习会话，请先开始会话"
            }
        
        print(f"\n📝 正在为学生推荐 {num_questions} 道题目...")
        result = self.engine.get_recommendations(self.current_session, num_questions)
        
        if result["status"] == "success":
            print(f"✅ 成功推荐 {len(result['recommendations'])} 道题目")
            print(f"📈 当前批次: {result['batch_number']}")
        else:
            print(f"❌ 题目推荐失败: {result['message']}")
        
        return result
    
    def submit_student_answers(self, answers: List[Dict]) -> Dict:
        """提交学生答案"""
        if not self.current_session:
            return {
                "status": "error",
                "message": "没有活跃的学习会话，请先开始会话"
            }
        
        print(f"\n📤 正在提交 {len(answers)} 个答案...")
        result = self.engine.submit_answers(self.current_session, answers)
        
        if result["status"] == "success":
            print(f"✅ 答案提交成功！")
            print(f"🎯 已完成批次: {result['batch_completed']}")
            
            # 显示答题详情
            if "answer_details" in result:
                correct_count = sum(1 for detail in result["answer_details"] if detail["correct"])
                total_count = len(result["answer_details"])
                accuracy = correct_count / total_count if total_count > 0 else 0
                
                print(f"📊 本批次答题情况: {correct_count}/{total_count} 正确 (准确率: {accuracy:.1%})")
                
                for detail in result["answer_details"]:
                    status_emoji = "✅" if detail["correct"] else "❌"
                    print(f"   {detail['qid']}: {detail['selected']} {status_emoji}")
                    if not detail["correct"]:
                        print(f"      正确答案: {detail['correct_answer']}")
            
            print(f"📊 更新后的知识点掌握度:")
            for kp, score in result["current_mastery"].items():
                print(f"   {kp}: {score:.3f}")
            
            mastered = result["mastered_knowledge_points"]
            if mastered:
                print(f"🏆 已掌握的知识点: {', '.join(mastered)}")
        else:
            print(f"❌ 答案提交失败: {result['message']}")
        
        return result
    
    def check_answers_only(self, answers: List[Dict]) -> Dict:
        """仅检查答案正确性，不更新学生模型"""
        return self.engine.check_answers(answers)
    
    def get_weak_points(self, threshold: float = 0.3) -> Dict:
        """获取当前学生的薄弱知识点"""
        if not self.current_session:
            return {
                "status": "error",
                "message": "没有活跃的学习会话，请先开始会话"
            }
        
        result = self.engine.get_weak_knowledge_points(self.current_session, threshold)
        
        if result["status"] == "success":
            print(f"\n🔍 学生 {self.current_session} 的薄弱知识点分析:")
            print("="*60)
            
            progress = result["progress_summary"]
            print(f"📊 学习进展总览:")
            print(f"   总知识点数: {progress['total_knowledge_points']}")
            print(f"   已掌握: {progress['mastered']} 个")
            print(f"   中等水平: {progress['moderate']} 个") 
            print(f"   薄弱: {progress['weak']} 个")
            print(f"   平均掌握度: {progress['average_mastery']:.3f}")
            
            if result["weak_knowledge_points"]:
                print(f"\n🔴 薄弱知识点详情:")
                for kp, score in result["weak_knowledge_points"]:
                    print(f"   {kp}: {score:.3f}")
            else:
                print(f"\n🎉 暂无明显薄弱知识点！")
            
            print(f"\n💡 学习建议:")
            for recommendation in result["recommendations"]:
                print(f"   {recommendation}")
        
        return result
    
    def get_session_status(self) -> Dict:
        """获取当前会话状态"""
        if not self.current_session:
            return {
                "status": "error",
                "message": "没有活跃的学习会话"
            }
        
        return self.engine.get_student_status(self.current_session)
    
    def end_session(self) -> Dict:
        """结束当前会话"""
        if not self.current_session:
            return {
                "status": "error",
                "message": "没有活跃的学习会话"
            }
        
        final_status = self.get_session_status()
        session_id = self.current_session
        self.current_session = None
        
        print(f"\n🏁 学习会话 {session_id} 已结束")
        if final_status["status"] == "success":
            print(f"📊 最终统计:")
            print(f"   总批次数: {final_status['batch_count']}")
            print(f"   总题目数: {final_status['total_questions']}")
            print(f"   掌握知识点: {len(final_status['mastered_knowledge_points'])}")
        
        return {
            "status": "success",
            "message": f"会话 {session_id} 已成功结束",
            "final_status": final_status
        }
    
    # ===== 数据持久化相关API =====
    
    def export_student_data(self, student_id: str = None) -> Dict:
        """导出学生数据用于持久化存储"""
        if student_id is None:
            student_id = self.current_session
        
        if not student_id:
            return {
                "status": "error",
                "message": "没有指定学生ID，且没有活跃的学习会话"
            }
        
        return self.engine.export_student_data(student_id)
    
    def import_student_data(self, student_data: Dict) -> Dict:
        """从持久化数据恢复学生"""
        return self.engine.import_student_data(student_data)
    
    def export_all_students(self) -> Dict:
        """导出所有学生数据"""
        return self.engine.export_all_students()
    
    def import_all_students(self, students_data: Dict) -> Dict:
        """批量恢复学生数据"""
        return self.engine.import_all_students(students_data)
    
    def get_students_list(self) -> Dict:
        """获取当前系统中所有学生的基本信息"""
        return self.engine.get_students_list()
    
    def clear_all_students(self) -> Dict:
        """清空所有学生数据（谨慎使用）"""
        return self.engine.clear_all_students()
    
    def save_student_to_file(self, student_id: str = None, file_path: str = None) -> Dict:
        """将学生数据保存到文件"""
        if student_id is None:
            student_id = self.current_session
        
        if not student_id:
            return {
                "status": "error",
                "message": "没有指定学生ID，且没有活跃的学习会话"
            }
        
        if file_path is None:
            file_path = f"student_data_{student_id}_{int(time.time())}.json"
        
        try:
            export_result = self.export_student_data(student_id)
            if export_result["status"] != "success":
                return export_result
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_result, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "student_id": student_id,
                "file_path": file_path,
                "message": f"学生 {student_id} 数据已保存到 {file_path}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存文件失败: {str(e)}"
            }
    
    def load_student_from_file(self, file_path: str) -> Dict:
        """从文件加载学生数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                student_data = json.load(f)
            
            import_result = self.import_student_data(student_data)
            if import_result["status"] == "success":
                import_result["file_path"] = file_path
                import_result["message"] += f"，数据来源: {file_path}"
            
            return import_result
            
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"文件不存在: {file_path}"
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": f"文件格式错误，不是有效的JSON: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"加载文件失败: {str(e)}"
            }
    
    def save_all_students_to_file(self, file_path: str = None) -> Dict:
        """将所有学生数据保存到文件"""
        if file_path is None:
            file_path = f"all_students_data_{int(time.time())}.json"
        
        try:
            export_result = self.export_all_students()
            if export_result["status"] != "success":
                return export_result
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_result, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "file_path": file_path,
                "student_count": export_result["student_count"],
                "message": f"已保存 {export_result['student_count']} 个学生的数据到 {file_path}"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"保存文件失败: {str(e)}"
            }
    
    def load_all_students_from_file(self, file_path: str) -> Dict:
        """从文件加载所有学生数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                students_data = json.load(f)
            
            import_result = self.import_all_students(students_data)
            if import_result["status"] in ["success", "partial"]:
                import_result["file_path"] = file_path
                import_result["message"] += f"，数据来源: {file_path}"
            
            return import_result
            
        except FileNotFoundError:
            return {
                "status": "error",
                "message": f"文件不存在: {file_path}"
            }
        except json.JSONDecodeError:
            return {
                "status": "error",
                "message": f"文件格式错误，不是有效的JSON: {file_path}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"加载文件失败: {str(e)}"
            }

def display_question(question: Dict, index: int) -> None:
    """显示题目"""
    print(f"\n{'='*60}")
    print(f"题目 {index + 1}: {question['content']}")
    print(f"{'='*60}")
    
    for i, option in enumerate(question['options']):
        print(f"{chr(65 + i)}. {option}")
    
    print(f"\n💡 涉及知识点: {', '.join(question['knowledge_points'].keys())}")
    print(f"🎯 难度系数: {question.get('difficulty', 0.5):.2f}")

def interactive_learning_session():
    """交互式学习会话"""
    api = EducationRecommendationAPI()
    
    print("\n" + "="*80)
    print("🎓 欢迎使用知识图谱智能推荐系统！")
    print("="*80)
    
    # 输入学生ID
    student_id = input("\n👤 请输入学生ID: ").strip()
    if not student_id:
        student_id = f"student_{np.random.randint(1000, 9999)}"
        print(f"🔄 使用默认ID: {student_id}")
    
    # 开始会话
    session_result = api.start_session(student_id)
    if session_result["status"] != "success":
        print("❌ 无法开始学习会话，程序退出")
        return
    
    batch_number = 1
    
    while True:
        print(f"\n{'='*80}")
        print(f"🎯 第 {batch_number} 批次学习")
        print("="*80)
        
        # 获取推荐题目
        recommendation_result = api.get_questions(3)
        if recommendation_result["status"] != "success":
            print("❌ 无法获取推荐题目")
            break
        
        questions = recommendation_result["recommendations"]
        if not questions:
            print("🎉 恭喜！没有更多适合的题目了，您的学习进展很好！")
            break
        
        # 显示题目并收集答案
        student_answers = []
        
        for i, question in enumerate(questions):
            display_question(question, i)
            
            while True:
                answer_input = input(f"\n您的答案 (A/B/C/D) 或 'q' 退出: ").strip().upper()
                
                if answer_input == 'Q':
                    print("👋 退出学习会话...")
                    api.end_session()
                    return
                
                if answer_input in ['A', 'B', 'C', 'D']:
                    # 使用新的答题格式，系统会自动判断对错
                    student_answers.append({
                        "qid": question["qid"],
                        "selected": answer_input
                    })
                    
                    print(f"📝 答案已记录: {answer_input}")
                    break
                else:
                    print("❗ 请输入有效答案 (A/B/C/D) 或 'q' 退出")
        
        # 提交答案
        submit_result = api.submit_student_answers(student_answers)
        if submit_result["status"] != "success":
            print("❌ 答案提交失败")
            break
        
        # 显示薄弱知识点分析
        if batch_number % 2 == 0:  # 每两个批次显示一次分析
            print(f"\n" + "="*60)
            print(f"📈 阶段性学习分析 (第 {batch_number} 批次)")
            print("="*60)
            api.get_weak_points()
        
        # 询问是否继续
        print(f"\n📈 本批次学习完成！")
        continue_choice = input("是否继续下一批次学习？(y/n): ").strip().lower()
        
        if continue_choice not in ['y', 'yes', '']:
            break
        
        batch_number += 1
    
    # 结束会话
    api.end_session()
    print("\n🎓 感谢使用知识图谱推荐系统！")

def run_demo_session():
    """运行演示会话"""
    print("\n🔥 运行演示会话...")
    
    api = EducationRecommendationAPI()
    
    # 创建演示学生
    demo_student_id = "demo_student_001"
    initial_mastery = {
        'K1': 0.2,  # 集合运算
        'K2': 0.15, # 关系映射  
        'K3': 0.1   # 图基本概念
    }
    
    session_result = api.start_session(demo_student_id, initial_mastery)
    
    # 模拟3轮学习
    for round_num in range(1, 4):
        print(f"\n🎯 演示第 {round_num} 轮:")
        
        # 获取推荐
        questions = api.get_questions(2)
        if questions["status"] != "success":
            break
        
        # 模拟答题
        demo_answers = []
        for q in questions["recommendations"]:
            # 模拟正确率70%
            import random
            
            # 随机选择一个选项 (A, B, C, D)
            selected_option = random.choice(['A', 'B', 'C', 'D'])
            
            demo_answers.append({
                "qid": q["qid"],
                "selected": selected_option
            })
        
        # 提交答案
        submit_result = api.submit_student_answers(demo_answers)
        
        if submit_result["status"] == "success":
            print(f"   📊 批次 {round_num} 完成")
    
    # 显示最终状态
    final_status = api.get_session_status()
    if final_status["status"] == "success":
        print(f"\n📈 演示完成！最终掌握 {len(final_status['mastered_knowledge_points'])} 个知识点")
    
    # 显示薄弱知识点分析
    print(f"\n🔍 最终学习分析:")
    api.get_weak_points()
    
    api.end_session()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "demo":
            run_demo_session()
        elif mode == "interactive":
            interactive_learning_session()
        elif mode == "api":
            print("🔧 API模式 - 请通过import方式使用EducationRecommendationAPI类")
            print("示例:")
            print("from start import EducationRecommendationAPI")
            print("api = EducationRecommendationAPI()")
        else:
            print("❗ 未知模式。可用模式: demo, interactive, api")
    else:
        print("\n🎓 知识图谱推荐系统")
        print("="*50)
        print("使用方法:")
        print("  python start.py demo        # 运行演示")
        print("  python start.py interactive # 交互式学习")
        print("  python start.py api         # API模式说明")
        print("\n或者直接运行交互式学习:")
        
        try:
            interactive_learning_session()
        except KeyboardInterrupt:
            print("\n\n👋 程序被用户中断，再见！")
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")

if __name__ == "__main__":
    # 添加numpy导入用于随机ID生成
    import numpy as np
    main()
