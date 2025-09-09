#!/usr/bin/env python3
"""
智能推荐引擎
基于学生学习数据和知识点掌握度进行智能题目推荐
"""

import random
import math
from typing import List, Dict, Tuple
from database import db

class IntelligentRecommendationEngine:
    """智能推荐引擎"""
    
    def __init__(self):
        self.questions_db = [
            {
                "questionId": "Q1",
                "description": "集合A={1,2,3}，集合B={2,3,4}，求A∪B",
                "knowledgePoint": "K1",
                "knowledgePointName": "集合运算",
                "options": [
                    {"id": "A", "text": "{1,2,3}"},
                    {"id": "B", "text": "{2,3}"},
                    {"id": "C", "text": "{1,2,3,4}"},
                    {"id": "D", "text": "{4}"}
                ],
                "correctAnswer": "C",
                "difficulty": 0.5,
                "score": 0.8
            },
            {
                "questionId": "Q2", 
                "description": "下列哪个是自反关系？",
                "knowledgePoint": "K2",
                "knowledgePointName": "关系映射",
                "options": [
                    {"id": "A", "text": "R={(1,1),(2,2)}"},
                    {"id": "B", "text": "R={(1,2),(2,1)}"},
                    {"id": "C", "text": "R={(1,1),(1,2)}"},
                    {"id": "D", "text": "R={(2,1)}"}
                ],
                "correctAnswer": "A",
                "difficulty": 0.6,
                "score": 0.7
            },
            {
                "questionId": "Q3",
                "description": "在有向图中，顶点的入度定义为？",
                "knowledgePoint": "K3", 
                "knowledgePointName": "图基本概念",
                "options": [
                    {"id": "A", "text": "指向该顶点的边数"},
                    {"id": "B", "text": "从该顶点出发的边数"},
                    {"id": "C", "text": "与该顶点相连的边数"},
                    {"id": "D", "text": "该顶点的标号"}
                ],
                "correctAnswer": "A",
                "difficulty": 0.4,
                "score": 0.9
            },
            {
                "questionId": "Q4",
                "description": "无向图G有6个顶点，每个顶点的度数都是3，那么图G有多少条边？",
                "knowledgePoint": "K8",
                "knowledgePointName": "度的概念",
                "options": [
                    {"id": "A", "text": "6条"},
                    {"id": "B", "text": "9条"},
                    {"id": "C", "text": "12条"},
                    {"id": "D", "text": "18条"}
                ],
                "correctAnswer": "B",
                "difficulty": 0.7,
                "score": 0.6
            },
            {
                "questionId": "Q5",
                "description": "完全图K5有多少条边？",
                "knowledgePoint": "K3",
                "knowledgePointName": "图基本概念",
                "options": [
                    {"id": "A", "text": "5条"},
                    {"id": "B", "text": "10条"},
                    {"id": "C", "text": "15条"},
                    {"id": "D", "text": "20条"}
                ],
                "correctAnswer": "B",
                "difficulty": 0.6,
                "score": 0.7
            },
            {
                "questionId": "Q6",
                "description": "集合A={1,2,3,4}，集合B={3,4,5,6}，求A∩B",
                "knowledgePoint": "K1",
                "knowledgePointName": "集合运算",
                "options": [
                    {"id": "A", "text": "{1,2,3,4}"},
                    {"id": "B", "text": "{3,4}"},
                    {"id": "C", "text": "{1,2,5,6}"},
                    {"id": "D", "text": "{1,2,3,4,5,6}"}
                ],
                "correctAnswer": "B",
                "difficulty": 0.4,
                "score": 0.8
            },
            {
                "questionId": "Q7",
                "description": "下列哪个关系是对称关系？",
                "knowledgePoint": "K2",
                "knowledgePointName": "关系映射",
                "options": [
                    {"id": "A", "text": "R={(1,1),(2,2)}"},
                    {"id": "B", "text": "R={(1,2),(2,1)}"},
                    {"id": "C", "text": "R={(1,1),(1,2)}"},
                    {"id": "D", "text": "R={(2,1)}"}
                ],
                "correctAnswer": "B",
                "difficulty": 0.5,
                "score": 0.7
            },
            {
                "questionId": "Q8",
                "description": "无向图G有n个顶点，m条边，那么所有顶点度数之和等于？",
                "knowledgePoint": "K8",
                "knowledgePointName": "度的概念",
                "options": [
                    {"id": "A", "text": "n"},
                    {"id": "B", "text": "m"},
                    {"id": "C", "text": "2m"},
                    {"id": "D", "text": "n+m"}
                ],
                "correctAnswer": "C",
                "difficulty": 0.6,
                "score": 0.8
            }
        ]
    
    def recommend_questions(self, student_id: str, knowledge_points: List[str] = None, 
                           num_questions: int = 3) -> Tuple[List[Dict], str]:
        """智能推荐题目"""
        try:
            # 确保学生存在
            if not self._ensure_student_exists(student_id):
                return [], "学生不存在"
            
            # 获取学生掌握度
            mastery = db.get_student_mastery(student_id)
            if not mastery:
                mastery = {"K1": 0.1, "K2": 0.1, "K3": 0.1, "K8": 0.1}
            
            # 获取推荐历史
            recommendation_history = db.get_recommendation_history(student_id, 20)
            recent_questions = {rec["questionId"] for rec in recommendation_history[-10:]}
            
            # 过滤题目
            if knowledge_points:
                # 针对特定知识点推荐
                candidate_questions = [q for q in self.questions_db 
                                     if q['knowledgePoint'] in knowledge_points]
                reason = f"针对知识点 {', '.join(knowledge_points)} 的专项练习"
            else:
                # 智能推荐
                candidate_questions = self._get_smart_recommendations(mastery, recent_questions)
                reason = self._get_recommendation_reason(mastery)
            
            # 计算推荐分数并排序
            scored_questions = []
            for question in candidate_questions:
                score = self._calculate_recommendation_score(
                    question, mastery, recent_questions
                )
                scored_questions.append((question, score))
            
            # 按分数排序，选择前N个
            scored_questions.sort(key=lambda x: x[1], reverse=True)
            recommended = [q[0] for q in scored_questions[:num_questions]]
            
            # 记录推荐历史
            for question in recommended:
                db.record_recommendation(student_id, question["questionId"], reason)
            
            print(f"🎯 为学生 {student_id} 推荐了 {len(recommended)} 道题目")
            print(f"📊 推荐原因: {reason}")
            
            return recommended, reason
            
        except Exception as e:
            print(f"❌ 推荐失败: {e}")
            return [], f"推荐失败: {str(e)}"
    
    def _ensure_student_exists(self, student_id: str) -> bool:
        """确保学生存在"""
        try:
            mastery = db.get_student_mastery(student_id)
            if not mastery:
                # 创建新学生
                db.create_student(student_id, student_id, f"{student_id}@example.com")
                return True
            return True
        except Exception as e:
            print(f"❌ 确保学生存在失败: {e}")
            return False
    
    def _get_smart_recommendations(self, mastery: Dict[str, float], 
                                 recent_questions: set) -> List[Dict]:
        """获取智能推荐题目"""
        recommendations = []
        
        # 1. 薄弱知识点优先 (掌握度 < 0.4)
        weak_points = [kp for kp, score in mastery.items() if score < 0.4]
        if weak_points:
            weak_questions = [q for q in self.questions_db 
                            if q['knowledgePoint'] in weak_points 
                            and q['questionId'] not in recent_questions]
            recommendations.extend(weak_questions)
        
        # 2. 中等掌握度知识点 (0.4 <= 掌握度 < 0.7)
        medium_points = [kp for kp, score in mastery.items() if 0.4 <= score < 0.7]
        if medium_points:
            medium_questions = [q for q in self.questions_db 
                              if q['knowledgePoint'] in medium_points 
                              and q['questionId'] not in recent_questions]
            recommendations.extend(medium_questions)
        
        # 3. 巩固已掌握知识点 (掌握度 >= 0.7)
        strong_points = [kp for kp, score in mastery.items() if score >= 0.7]
        if strong_points:
            strong_questions = [q for q in self.questions_db 
                              if q['knowledgePoint'] in strong_points 
                              and q['questionId'] not in recent_questions]
            recommendations.extend(strong_questions)
        
        # 4. 如果都没有，返回所有题目
        if not recommendations:
            recommendations = [q for q in self.questions_db 
                            if q['questionId'] not in recent_questions]
        
        return recommendations
    
    def _calculate_recommendation_score(self, question: Dict, mastery: Dict[str, float],
                                     recent_questions: set) -> float:
        """计算推荐分数"""
        score = 0.0
        
        # 基础分数
        score += question.get('score', 0.5) * 0.3
        
        # 知识点掌握度权重
        kp = question['knowledgePoint']
        mastery_score = mastery.get(kp, 0.1)
        
        # 薄弱知识点优先
        if mastery_score < 0.4:
            score += 0.4  # 薄弱知识点高权重
        elif mastery_score < 0.7:
            score += 0.2  # 中等掌握度中等权重
        else:
            score += 0.1  # 已掌握知识点低权重
        
        # 难度适应性
        difficulty = question.get('difficulty', 0.5)
        if mastery_score < 0.3 and difficulty > 0.6:
            score -= 0.2  # 避免给初学者推荐过难题目
        elif mastery_score > 0.7 and difficulty < 0.4:
            score -= 0.1  # 避免给高手推荐过简单题目
        
        # 避免重复推荐
        if question['questionId'] in recent_questions:
            score -= 0.3
        
        # 随机因子，增加多样性
        score += random.uniform(-0.1, 0.1)
        
        return max(0.0, score)
    
    def _get_recommendation_reason(self, mastery: Dict[str, float]) -> str:
        """获取推荐原因"""
        weak_points = [kp for kp, score in mastery.items() if score < 0.4]
        medium_points = [kp for kp, score in mastery.items() if 0.4 <= score < 0.7]
        
        if weak_points:
            return f"检测到薄弱知识点 {', '.join(weak_points)}，优先推荐相关练习"
        elif medium_points:
            return f"针对中等掌握度知识点 {', '.join(medium_points)} 进行巩固练习"
        else:
            return "基于您的学习情况，推荐综合练习题目"
    
    def get_adaptive_difficulty(self, student_id: str, knowledge_point: str) -> float:
        """获取自适应难度"""
        try:
            mastery = db.get_student_mastery(student_id)
            base_mastery = mastery.get(knowledge_point, 0.1)
            
            # 基于掌握度调整难度
            if base_mastery < 0.3:
                return random.uniform(0.3, 0.5)  # 初学者：简单题目
            elif base_mastery < 0.6:
                return random.uniform(0.4, 0.7)  # 中等水平：中等难度
            else:
                return random.uniform(0.5, 0.8)  # 高水平：较难题目
        except Exception as e:
            print(f"❌ 获取自适应难度失败: {e}")
            return 0.5
    
    def analyze_learning_pattern(self, student_id: str) -> Dict:
        """分析学习模式"""
        try:
            stats = db.get_student_statistics(student_id)
            weak_points = db.get_weak_knowledge_points(student_id)
            trend = db.get_learning_trend(student_id, 7)
            
            # 分析学习模式
            pattern = {
                "learningStyle": "balanced",  # balanced, weak_focused, strong_focused
                "difficultyPreference": "medium",  # easy, medium, hard
                "studyFrequency": "regular",  # regular, irregular, intensive
                "weakestArea": None,
                "strongestArea": None,
                "recommendations": []
            }
            
            if weak_points:
                pattern["weakestArea"] = weak_points[0]["name"]
                pattern["learningStyle"] = "weak_focused"
                pattern["recommendations"].append("建议加强薄弱知识点的专项练习")
            
            if stats.get("recentAccuracy", 0) > 80:
                pattern["difficultyPreference"] = "hard"
                pattern["recommendations"].append("可以尝试更有挑战性的题目")
            elif stats.get("recentAccuracy", 0) < 50:
                pattern["difficultyPreference"] = "easy"
                pattern["recommendations"].append("建议从基础题目开始巩固")
            
            if len(trend) >= 5:
                pattern["studyFrequency"] = "regular"
            elif len(trend) < 2:
                pattern["studyFrequency"] = "irregular"
                pattern["recommendations"].append("建议保持更规律的学习节奏")
            
            return pattern
        except Exception as e:
            print(f"❌ 分析学习模式失败: {e}")
            return {}

# 全局推荐引擎实例
recommendation_engine = IntelligentRecommendationEngine()
