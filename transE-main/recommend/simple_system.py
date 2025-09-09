#!/usr/bin/env python3
"""
知识图谱推荐系统核心逻辑
为前端提供标准化的推荐服务
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import json
import pandas as pd
import time
from typing import Dict, List, Tuple, Optional

class StudentModel:
    """学生模型类"""
    
    def __init__(self, student_id: str, initial_mastery: Optional[Dict[str, float]] = None, embedding_dim: int = 50):
        self.student_id = student_id
        self.embedding_dim = embedding_dim
        
        # 初始化掌握度
        if initial_mastery is None:
            self.mastery_scores = {
                'K1': 0.1,  # 集合运算
                'K2': 0.1,  # 关系映射
                'K3': 0.05, # 图基本概念
            }
        else:
            self.mastery_scores = initial_mastery.copy()
        
        # 学习历史
        self.vector = None
        self.question_history = []
        self.batch_count = 0
        self.vector_history = []
    
    def initialize_vector_from_mastery(self, embeddings: Dict[str, np.ndarray]) -> None:
        """从知识点掌握度计算初始学生向量"""
        weighted_vector = np.zeros(self.embedding_dim)
        total_weight = 0
        
        for kp_id, mastery_score in self.mastery_scores.items():
            if kp_id in embeddings and mastery_score > 0:
                weighted_vector += mastery_score * embeddings[kp_id]
                total_weight += mastery_score
        
        if total_weight > 0:
            self.vector = weighted_vector / total_weight
        else:
            self.vector = np.random.normal(0, 0.1, self.embedding_dim)
        
        # 归一化向量
        if np.linalg.norm(self.vector) > 0:
            self.vector = self.vector / np.linalg.norm(self.vector)
        
        self.vector_history = [self.vector.copy()]
    
    def update_from_answers(self, answers: List[Dict], embeddings: Dict[str, np.ndarray], alpha: float = 0.7) -> None:
        """根据答题情况更新学生模型"""
        # 计算批次向量
        batch_vector = self._compute_batch_vector(answers, embeddings)
        
        # 更新学生向量
        if self.batch_count == 0:
            self.vector = batch_vector
        else:
            self.vector = alpha * self.vector + (1 - alpha) * batch_vector
        
        # 归一化
        if np.linalg.norm(self.vector) > 0:
            self.vector = self.vector / np.linalg.norm(self.vector)
        
        # 更新掌握度
        self._update_mastery_scores(answers)
        
        # 记录历史
        self.question_history.extend(answers)
        self.vector_history.append(self.vector.copy())
        self.batch_count += 1
    
    def _compute_batch_vector(self, answers: List[Dict], embeddings: Dict[str, np.ndarray]) -> np.ndarray:
        """计算单批次的学习向量"""
        batch_vector = np.zeros(self.embedding_dim)
        
        for answer in answers:
            for kp_id, weight in answer["knowledge_points"].items():
                if kp_id in embeddings:
                    kp_embedding = embeddings[kp_id]
                    if answer["correct"]:
                        learning_strength = 1.0 * weight
                    else:
                        learning_strength = 0.3 * weight
                    batch_vector += learning_strength * kp_embedding
        
        if len(answers) > 0:
            batch_vector /= len(answers)
        
        return batch_vector
    
    def _update_mastery_scores(self, answers: List[Dict]) -> None:
        """更新知识点掌握度"""
        for answer in answers:
            for kp_id, weight in answer["knowledge_points"].items():
                if kp_id not in self.mastery_scores:
                    self.mastery_scores[kp_id] = 0.0
                
                if answer["correct"]:
                    delta = 0.3 * weight
                    self.mastery_scores[kp_id] = min(1.0, self.mastery_scores[kp_id] + delta)
                else:
                    delta = 0.1 * weight
                    self.mastery_scores[kp_id] = min(1.0, self.mastery_scores[kp_id] + delta)
    
    def get_mastered_knowledge_points(self, threshold: float = 0.5) -> List[str]:
        """获取已掌握的知识点"""
        return [kp for kp, score in self.mastery_scores.items() if score >= threshold]
    
    def get_mastery_level(self, kp_id: str) -> float:
        """获取单个知识点掌握程度"""
        return self.mastery_scores.get(kp_id, 0.0)
    
    def get_weak_knowledge_points(self, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """获取薄弱知识点列表，按掌握度从低到高排序"""
        weak_points = [(kp, score) for kp, score in self.mastery_scores.items() 
                      if score < threshold]
        weak_points.sort(key=lambda x: x[1])  # 按掌握度从低到高排序
        return weak_points
    
    def get_learning_progress_summary(self) -> Dict:
        """获取学习进展总结"""
        mastered = self.get_mastered_knowledge_points(threshold=0.5)
        weak = self.get_weak_knowledge_points(threshold=0.3)
        moderate = [(kp, score) for kp, score in self.mastery_scores.items() 
                   if 0.3 <= score < 0.5]
        
        return {
            "total_knowledge_points": len(self.mastery_scores),
            "mastered": len(mastered),
            "moderate": len(moderate),
            "weak": len(weak),
            "mastered_list": mastered,
            "weak_list": [kp for kp, _ in weak],
            "average_mastery": sum(self.mastery_scores.values()) / len(self.mastery_scores) if self.mastery_scores else 0
        }
    
    def export_data(self) -> Dict:
        """导出学生数据用于持久化存储"""
        export_data = {
            "student_id": self.student_id,
            "embedding_dim": self.embedding_dim,
            "mastery_scores": self.mastery_scores.copy(),
            "question_history": self.question_history.copy(),
            "batch_count": self.batch_count,
            "export_timestamp": time.time(),
            "version": "1.1"  # 数据格式版本
        }
        
        # 导出向量数据（转换为列表以便JSON序列化）
        if self.vector is not None:
            export_data["vector"] = self.vector.tolist()
        else:
            export_data["vector"] = None
            
        # 导出向量历史（转换为列表）
        if self.vector_history:
            export_data["vector_history"] = [v.tolist() for v in self.vector_history]
        else:
            export_data["vector_history"] = []
        
        return export_data
    
    @classmethod
    def from_data(cls, student_data: Dict, validate: bool = True):
        """从导出的数据创建学生对象"""
        if validate:
            # 验证数据完整性
            required_fields = ["student_id", "mastery_scores", "question_history"]
            for field in required_fields:
                if field not in student_data:
                    raise ValueError(f"学生数据缺少必要字段: {field}")
        
        # 创建学生对象
        student_id = student_data["student_id"]
        initial_mastery = student_data.get("mastery_scores", {})
        embedding_dim = student_data.get("embedding_dim", 50)
        
        student = cls(student_id, initial_mastery, embedding_dim)
        
        # 恢复历史数据
        student.question_history = student_data.get("question_history", [])
        student.batch_count = student_data.get("batch_count", 0)
        
        # 恢复向量数据
        if student_data.get("vector") is not None:
            student.vector = np.array(student_data["vector"])
        
        # 恢复向量历史
        if student_data.get("vector_history"):
            student.vector_history = [np.array(v) for v in student_data["vector_history"]]
        
        return student

class RecommendationSystem:
    """推荐系统类"""
    
    def __init__(self, embeddings_path: str, knowledge_graph_path: str, question_bank_path: str):
        # 加载数据
        self.embeddings = self._load_embeddings(embeddings_path)
        self.knowledge_graph = self._load_knowledge_graph(knowledge_graph_path)
        self.questions = self._load_questions(question_bank_path)
        
        # 初始化关系向量
        self.relation_embeddings = self._initialize_relation_vectors()
    
    def _load_embeddings(self, path: str) -> Dict[str, np.ndarray]:
        """加载知识点嵌入向量"""
        df = pd.read_csv(path)
        embeddings = {}
        for _, row in df.iterrows():
            kp_id = row['kp_id']
            vector = row.iloc[1:].values.astype(float)
            embeddings[kp_id] = vector
        return embeddings
    
    def _load_knowledge_graph(self, path: str) -> pd.DataFrame:
        """加载知识图谱"""
        return pd.read_csv(path)
    
    def _load_questions(self, path: str) -> List[Dict]:
        """加载题库"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['questions']
    
    def _initialize_relation_vectors(self) -> Dict[str, np.ndarray]:
        """初始化关系向量"""
        np.random.seed(42)
        prerequisite_vector = np.random.normal(0.1, 0.15, 50)
        related_vector = np.random.normal(0, 0.05, 50)
        
        return {
            "is_prerequisite_for": prerequisite_vector / np.linalg.norm(prerequisite_vector),
            "is_related_to": related_vector / np.linalg.norm(related_vector)
        }
    
    def check_answer(self, qid: str, selected_answer: str) -> Dict:
        """检查答题是否正确"""
        question = self.get_question_by_id(qid)
        if not question:
            return {
                "status": "error",
                "message": f"题目 {qid} 不存在"
            }
        
        correct_answer = question["answer"]
        
        # 处理选项映射 (A->第0个选项, B->第1个选项...)
        option_map = {chr(65 + i): option for i, option in enumerate(question["options"])}
        selected_option = option_map.get(selected_answer.upper())
        
        is_correct = False
        if selected_option == correct_answer:
            is_correct = True
        elif selected_answer.upper() in ['A', 'B', 'C', 'D']:
            # 直接字母选择判断
            correct_letter = None
            for i, option in enumerate(question["options"]):
                if option == correct_answer:
                    correct_letter = chr(65 + i)
                    break
            is_correct = (selected_answer.upper() == correct_letter)
        
        return {
            "status": "success",
            "qid": qid,
            "selected": selected_answer.upper(),
            "selected_option": selected_option,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "knowledge_points": question["knowledge_points"]
        }
    
    def get_question_by_id(self, qid: str) -> Optional[Dict]:
        """根据题目ID获取题目信息"""
        for question in self.questions:
            if question["qid"] == qid:
                return question
        return None
    
    def batch_check_answers(self, answer_submissions: List[Dict]) -> List[Dict]:
        """批量检查答题结果
        
        Args:
            answer_submissions: [{"qid": "Q1", "selected": "A"}, ...]
            
        Returns:
            检查结果列表
        """
        results = []
        for submission in answer_submissions:
            qid = submission.get("qid")
            selected = submission.get("selected")
            
            if not qid or not selected:
                results.append({
                    "status": "error",
                    "message": "缺少必要字段 qid 或 selected"
                })
                continue
            
            check_result = self.check_answer(qid, selected)
            results.append(check_result)
        
        return results
    
    def recommend_questions(self, student: StudentModel, num_questions: int = 3) -> List[Dict]:
        """为学生推荐题目"""
        mastered_kps = student.get_mastered_knowledge_points(threshold=0.1)
        
        if not mastered_kps:
            # 冷启动推荐
            return self._cold_start_recommend(student, num_questions)
        
        # 向量推理推荐
        return self._vector_based_recommend(student, num_questions)
    
    def _cold_start_recommend(self, student: StudentModel, num_questions: int) -> List[Dict]:
        """冷启动推荐"""
        basic_questions = []
        attempted = [ans['qid'] for ans in student.question_history]
        
        for q in self.questions:
            if q['qid'] in attempted:
                continue
            if any(kp in ['K1', 'K2', 'K3'] for kp in q['knowledge_points'].keys()):
                basic_questions.append(q)
        
        return basic_questions[:num_questions]
    
    def _vector_based_recommend(self, student: StudentModel, num_questions: int) -> List[Dict]:
        """基于向量推理的推荐"""
        mastered_kps = student.get_mastered_knowledge_points(threshold=0.1)
        best_mastered = max(mastered_kps, key=lambda kp: student.get_mastery_level(kp))
        
        # 向量推理
        V_mastered = self.embeddings[best_mastered]
        V_target = V_mastered + self.relation_embeddings["is_prerequisite_for"]
        
        # 找到候选知识点
        candidates = []
        for kp_id, kp_embedding in self.embeddings.items():
            if student.get_mastery_level(kp_id) < 0.5:
                similarity = cosine_similarity([V_target], [kp_embedding])[0][0]
                candidates.append((kp_id, similarity))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        # 收集候选题目
        candidate_questions = []
        attempted = [ans['qid'] for ans in student.question_history]
        target_question_count = 8
        
        for kp_id, kp_similarity in candidates:
            if len(candidate_questions) >= target_question_count:
                break
            
            for q in self.questions:
                if len(candidate_questions) >= target_question_count:
                    break
                
                if q['qid'] in attempted:
                    continue
                
                if kp_id in q['knowledge_points']:
                    if not any(cq['question']['qid'] == q['qid'] for cq in candidate_questions):
                        candidate_questions.append({
                            'question': q,
                            'target_kp': kp_id,
                            'kp_similarity': kp_similarity
                        })
        
        # 综合评分
        scored_questions = []
        for cq in candidate_questions:
            question = cq['question']
            target_kp = cq['target_kp']
            kp_similarity = cq['kp_similarity']
            
            coverage_score = question['knowledge_points'].get(target_kp, 0)
            relevance_score = kp_similarity
            difficulty_score = 1 - abs(question.get('difficulty', 0.5) - 0.6)
            diversity_score = len(question['knowledge_points']) * 0.1
            
            final_score = (
                0.4 * coverage_score +
                0.3 * relevance_score +
                0.2 * difficulty_score +
                0.1 * diversity_score
            )
            
            scored_questions.append((question, final_score))
        
        # 排序并返回前N个
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        return [q for q, _ in scored_questions[:num_questions]]

class KnowledgeGraphRecommendationEngine:
    """知识图谱推荐引擎 - 主要接口类"""
    
    def __init__(self, config_path: str = None):
        """初始化推荐引擎"""
        # 默认配置
        self.embeddings_path = "embeddings.csv"
        self.knowledge_graph_path = "knowledge_graph.csv" 
        self.question_bank_path = "question_bank.json"
        
        # 加载配置
        if config_path:
            self._load_config(config_path)
        
        # 初始化推荐系统
        self.recommender = RecommendationSystem(
            self.embeddings_path,
            self.knowledge_graph_path,
            self.question_bank_path
        )
        
        # 存储学生模型
        self.students = {}
    
    def _load_config(self, config_path: str) -> None:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        self.embeddings_path = config.get('embeddings_path', self.embeddings_path)
        self.knowledge_graph_path = config.get('knowledge_graph_path', self.knowledge_graph_path)
        self.question_bank_path = config.get('question_bank_path', self.question_bank_path)
    
    def create_student(self, student_id: str, initial_mastery: Optional[Dict[str, float]] = None) -> Dict:
        """创建新学生"""
        student = StudentModel(student_id, initial_mastery)
        student.initialize_vector_from_mastery(self.recommender.embeddings)
        self.students[student_id] = student
        
        return {
            "status": "success",
            "student_id": student_id,
            "initial_mastery": student.mastery_scores,
            "message": f"学生 {student_id} 创建成功"
        }
    
    def get_recommendations(self, student_id: str, num_questions: int = 3) -> Dict:
        """获取推荐题目"""
        if student_id not in self.students:
            return {
                "status": "error",
                "message": f"学生 {student_id} 不存在"
            }
        
        student = self.students[student_id]
        recommended_questions = self.recommender.recommend_questions(student, num_questions)
        
        # 格式化返回结果
        formatted_questions = []
        for q in recommended_questions:
            formatted_questions.append({
                "qid": q["qid"],
                "content": q["content"],
                "options": q["options"],
                "knowledge_points": q["knowledge_points"],
                "difficulty": q.get("difficulty", 0.5)
            })
        
        return {
            "status": "success",
            "student_id": student_id,
            "recommendations": formatted_questions,
            "batch_number": student.batch_count + 1
        }
    
    def submit_answers(self, student_id: str, answers: List[Dict]) -> Dict:
        """提交答题结果"""
        if student_id not in self.students:
            return {
                "status": "error",
                "message": f"学生 {student_id} 不存在"
            }
        
        student = self.students[student_id]
        
        # 验证并处理答案格式
        processed_answers = []
        for answer in answers:
            if "qid" in answer and "selected" in answer:
                # 新格式：需要检查答案
                check_result = self.recommender.check_answer(answer["qid"], answer["selected"])
                if check_result["status"] == "error":
                    return {
                        "status": "error",
                        "message": check_result["message"]
                    }
                
                processed_answers.append({
                    "qid": check_result["qid"],
                    "correct": check_result["is_correct"],
                    "knowledge_points": check_result["knowledge_points"],
                    "selected": check_result["selected"],
                    "correct_answer": check_result["correct_answer"]
                })
            else:
                # 旧格式：已经包含correct字段
                required_fields = ["qid", "correct", "knowledge_points"]
                if not all(field in answer for field in required_fields):
                    return {
                        "status": "error",
                        "message": f"答案格式错误，需要包含字段: {required_fields}"
                    }
                processed_answers.append(answer)
        
        # 更新学生模型
        student.update_from_answers(processed_answers, self.recommender.embeddings)
        
        return {
            "status": "success",
            "student_id": student_id,
            "batch_completed": student.batch_count,
            "current_mastery": student.mastery_scores,
            "mastered_knowledge_points": student.get_mastered_knowledge_points(),
            "answer_details": processed_answers
        }
    
    def check_answers(self, answer_submissions: List[Dict]) -> Dict:
        """检查答题结果（不更新学生模型）"""
        results = self.recommender.batch_check_answers(answer_submissions)
        
        correct_count = sum(1 for r in results if r.get("is_correct", False))
        total_count = len(results)
        
        return {
            "status": "success",
            "total_questions": total_count,
            "correct_count": correct_count,
            "accuracy": correct_count / total_count if total_count > 0 else 0,
            "details": results
        }
    
    def get_weak_knowledge_points(self, student_id: str, threshold: float = 0.3) -> Dict:
        """获取学生的薄弱知识点"""
        if student_id not in self.students:
            return {
                "status": "error",
                "message": f"学生 {student_id} 不存在"
            }
        
        student = self.students[student_id]
        weak_points = student.get_weak_knowledge_points(threshold)
        progress_summary = student.get_learning_progress_summary()
        
        return {
            "status": "success",
            "student_id": student_id,
            "weak_knowledge_points": weak_points,
            "progress_summary": progress_summary,
            "recommendations": self._get_weak_point_recommendations(weak_points)
        }
    
    def _get_weak_point_recommendations(self, weak_points: List[Tuple[str, float]]) -> List[str]:
        """根据薄弱知识点生成学习建议"""
        recommendations = []
        
        if not weak_points:
            recommendations.append("🎉 恭喜！目前没有明显的薄弱知识点，继续保持！")
            return recommendations
        
        # 获取最薄弱的3个知识点
        top_weak = weak_points[:3]
        
        for kp, score in top_weak:
            if score < 0.1:
                recommendations.append(f"🔴 {kp} 掌握度极低({score:.2f})，建议重点学习基础概念")
            elif score < 0.2:
                recommendations.append(f"🟡 {kp} 掌握度较低({score:.2f})，需要加强练习")
            else:
                recommendations.append(f"🟠 {kp} 掌握度一般({score:.2f})，可以适量练习巩固")
        
        # 添加学习策略建议
        if len(weak_points) > 5:
            recommendations.append("💡 建议：薄弱知识点较多，建议循序渐进，先攻克最薄弱的2-3个知识点")
        elif len(weak_points) > 2:
            recommendations.append("💡 建议：可以同时学习多个薄弱知识点，但要注意合理分配时间")
        else:
            recommendations.append("💡 建议：集中精力攻克这些薄弱知识点，很快就能看到明显进步")
        
        return recommendations
    
    def get_student_status(self, student_id: str) -> Dict:
        """获取学生当前状态"""
        if student_id not in self.students:
            return {
                "status": "error",
                "message": f"学生 {student_id} 不存在"
            }
        
        student = self.students[student_id]
        
        return {
            "status": "success",
            "student_id": student_id,
            "batch_count": student.batch_count,
            "total_questions": len(student.question_history),
            "mastery_scores": student.mastery_scores,
            "mastered_knowledge_points": student.get_mastered_knowledge_points(),
            "vector_norm": float(np.linalg.norm(student.vector)) if student.vector is not None else 0.0
        }
    
    def export_student_data(self, student_id: str) -> Dict:
        """导出指定学生的数据用于持久化存储"""
        if student_id not in self.students:
            return {
                "status": "error",
                "message": f"学生 {student_id} 不存在"
            }
        
        student = self.students[student_id]
        student_data = student.export_data()
        
        return {
            "status": "success",
            "student_id": student_id,
            "data": student_data,
            "export_timestamp": time.time(),
            "message": f"学生 {student_id} 数据导出成功"
        }
    
    def import_student_data(self, student_data: Dict) -> Dict:
        """从持久化数据恢复学生对象"""
        try:
            # 验证数据格式
            if "data" in student_data:
                # 如果是通过export_student_data导出的格式
                actual_data = student_data["data"]
            else:
                # 如果直接是学生数据
                actual_data = student_data
            
            # 创建学生对象
            student = StudentModel.from_data(actual_data)
            
            # 重新初始化向量（如果需要）
            if student.vector is None and hasattr(self, 'recommender'):
                student.initialize_vector_from_mastery(self.recommender.embeddings)
            
            # 存储到内存中
            self.students[student.student_id] = student
            
            return {
                "status": "success",
                "student_id": student.student_id,
                "batch_count": student.batch_count,
                "total_questions": len(student.question_history),
                "message": f"学生 {student.student_id} 数据恢复成功"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"数据恢复失败: {str(e)}"
            }
    
    def export_all_students(self) -> Dict:
        """导出所有学生数据"""
        if not self.students:
            return {
                "status": "success",
                "data": {},
                "student_count": 0,
                "export_timestamp": time.time(),
                "message": "没有学生数据需要导出"
            }
        
        all_student_data = {}
        for student_id, student in self.students.items():
            all_student_data[student_id] = student.export_data()
        
        return {
            "status": "success",
            "data": all_student_data,
            "student_count": len(all_student_data),
            "export_timestamp": time.time(),
            "message": f"成功导出 {len(all_student_data)} 个学生的数据"
        }
    
    def import_all_students(self, students_data: Dict) -> Dict:
        """批量恢复学生数据"""
        success_count = 0
        error_count = 0
        errors = []
        
        # 清空现有学生数据
        self.students.clear()
        
        # 处理数据格式
        if "data" in students_data:
            # 如果是通过export_all_students导出的格式
            actual_data = students_data["data"]
        else:
            # 如果直接是学生数据字典
            actual_data = students_data
        
        for student_id, student_data in actual_data.items():
            try:
                student = StudentModel.from_data(student_data)
                
                # 重新初始化向量（如果需要）
                if student.vector is None and hasattr(self, 'recommender'):
                    student.initialize_vector_from_mastery(self.recommender.embeddings)
                
                self.students[student_id] = student
                success_count += 1
                
            except Exception as e:
                error_count += 1
                errors.append(f"学生 {student_id}: {str(e)}")
        
        return {
            "status": "success" if error_count == 0 else "partial",
            "success_count": success_count,
            "error_count": error_count,
            "errors": errors,
            "message": f"成功恢复 {success_count} 个学生，失败 {error_count} 个"
        }
    
    def clear_all_students(self) -> Dict:
        """清空所有学生数据（谨慎使用）"""
        student_count = len(self.students)
        self.students.clear()
        
        return {
            "status": "success",
            "cleared_count": student_count,
            "message": f"已清空 {student_count} 个学生的数据"
        }
    
    def get_students_list(self) -> Dict:
        """获取当前系统中所有学生的基本信息"""
        students_info = []
        
        for student_id, student in self.students.items():
            progress = student.get_learning_progress_summary()
            students_info.append({
                "student_id": student_id,
                "batch_count": student.batch_count,
                "total_questions": len(student.question_history),
                "mastered_knowledge_points": progress["mastered"],
                "average_mastery": progress["average_mastery"],
                "last_activity": max([q.get("timestamp", 0) for q in student.question_history]) if student.question_history else None
            })
        
        return {
            "status": "success",
            "students": students_info,
            "total_count": len(students_info),
            "message": f"当前系统中有 {len(students_info)} 个学生"
        }
