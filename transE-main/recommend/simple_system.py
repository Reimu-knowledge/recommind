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
    
    def __init__(self, embeddings_path: str, knowledge_graph_path: str, question_bank_path: str, node_names_path: str):
        # 加载数据
        self.embeddings = self._load_embeddings(embeddings_path)
        self.knowledge_graph = self._load_knowledge_graph(knowledge_graph_path)
        self.questions = self._load_questions(question_bank_path)
        self.node_names = self._load_node_names(node_names_path)
        print(self.node_names)
        
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

    def _load_node_names(self, path: str) -> Dict[str, str]:
        """加载节点名称映射"""
        df = pd.read_csv(path)
        # print(df.head())  # 打印列名以确认
        return pd.Series(df['id'].values, index=df['name']).to_dict()  # 修改为实际列名

    def _get_node_name(self, kp_id: str) -> str:
        """获取知识点名称"""
        return self.node_names.get(kp_id, kp_id)
    
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
        """基于向量推理的智能推荐 - 增强版"""
        # 分析学生学习状态
        learning_state = self._analyze_student_learning_state(student)
        
        # 根据学习状态选择推荐策略
        primary_strategy = self._determine_recommendation_strategy(learning_state)
        
        # 新增：动态混合策略
        if student.batch_count > 3:  # 有足够历史数据时采用混合策略
            return self._mixed_strategy_recommend(student, num_questions, learning_state, primary_strategy)
        else:
            # 执行单一策略
            if primary_strategy == "consolidation":
                return self._consolidation_recommend(student, num_questions, learning_state)
            elif primary_strategy == "gap_filling":
                return self._gap_filling_recommend(student, num_questions, learning_state)
            elif primary_strategy == "expansion":
                return self._expansion_recommend(student, num_questions, learning_state)
            else:  # balanced
                return self._balanced_recommend(student, num_questions, learning_state)
    
    def _mixed_strategy_recommend(self, student: StudentModel, num_questions: int, 
                                learning_state: Dict, primary_strategy: str) -> List[Dict]:
        """混合策略推荐：结合多种策略的优势"""
        recommendations = []
        
        # 计算各策略的题目分配比例
        if primary_strategy == "gap_filling":
            strategy_ratios = {"gap_filling": 0.6, "consolidation": 0.3, "balanced": 0.1}
        elif primary_strategy == "expansion":
            strategy_ratios = {"expansion": 0.6, "consolidation": 0.2, "balanced": 0.2}
        elif primary_strategy == "consolidation":
            strategy_ratios = {"consolidation": 0.5, "gap_filling": 0.3, "expansion": 0.2}
        else:  # balanced
            strategy_ratios = {"balanced": 0.4, "consolidation": 0.3, "gap_filling": 0.2, "expansion": 0.1}
        
        # 按比例分配题目数量
        remaining_questions = num_questions
        strategy_allocations = {}
        
        for strategy, ratio in strategy_ratios.items():
            allocated = max(1, round(num_questions * ratio)) if remaining_questions > 0 else 0
            allocated = min(allocated, remaining_questions)
            strategy_allocations[strategy] = allocated
            remaining_questions -= allocated
        
        # 分配剩余题目给主策略
        if remaining_questions > 0:
            strategy_allocations[primary_strategy] = strategy_allocations.get(primary_strategy, 0) + remaining_questions
        
        # 执行各策略并合并结果
        all_candidates = []
        
        for strategy, count in strategy_allocations.items():
            if count > 0:
                if strategy == "gap_filling":
                    strategy_recommendations = self._gap_filling_recommend(student, count, learning_state)
                elif strategy == "expansion":
                    strategy_recommendations = self._expansion_recommend(student, count, learning_state)
                elif strategy == "consolidation":
                    strategy_recommendations = self._consolidation_recommend(student, count, learning_state)
                else:  # balanced
                    strategy_recommendations = self._balanced_recommend(student, count, learning_state)
                
                # 为每个推荐题目添加策略来源标记
                for rec in strategy_recommendations:
                    rec['strategy_source'] = strategy
                    rec['is_mixed_strategy'] = True
                
                all_candidates.extend(strategy_recommendations)
        
        # 去重（避免不同策略推荐相同题目）
        seen_qids = set()
        final_recommendations = []
        
        for rec in all_candidates:
            if rec['qid'] not in seen_qids:
                seen_qids.add(rec['qid'])
                final_recommendations.append(rec)
        
        # 如果去重后题目不够，用平衡策略补充
        while len(final_recommendations) < num_questions:
            additional = self._balanced_recommend(student, num_questions - len(final_recommendations), learning_state)
            for rec in additional:
                if rec['qid'] not in seen_qids:
                    rec['strategy_source'] = 'supplement'
                    rec['is_mixed_strategy'] = True
                    final_recommendations.append(rec)
                    seen_qids.add(rec['qid'])
                    break
            else:
                break  # 没有更多可用题目
        
        return final_recommendations[:num_questions]
    
    def _analyze_student_learning_state(self, student: StudentModel) -> Dict:
        """分析学生学习状态 - 增强版"""
        mastery_scores = student.mastery_scores
        weak_points = student.get_weak_knowledge_points(threshold=0.3)
        mastered_points = student.get_mastered_knowledge_points(threshold=0.5)
        moderate_points = [(kp, score) for kp, score in mastery_scores.items() 
                          if 0.3 <= score < 0.5]
        
        # 计算学习进展指标
        total_kps = len(mastery_scores)
        avg_mastery = sum(mastery_scores.values()) / total_kps if total_kps > 0 else 0
        mastery_variance = np.var(list(mastery_scores.values())) if mastery_scores else 0
        
        # 分析最近答题表现（最近5题）
        recent_questions = student.question_history[-5:] if len(student.question_history) >= 5 else student.question_history
        recent_accuracy = sum(1 for q in recent_questions if q.get('correct', False)) / len(recent_questions) if recent_questions else 0
        
        # 新增：计算学习趋势
        learning_trend = self._calculate_learning_trend(student)
        
        # 新增：计算当前学习能力水平
        current_ability_level = self._estimate_ability_level(student)
        
        # 新增：分析知识点关联性
        knowledge_connectivity = self._analyze_knowledge_connectivity(mastered_points, weak_points)
        
        return {
            'weak_points': weak_points,
            'mastered_points': mastered_points,
            'moderate_points': moderate_points,
            'avg_mastery': avg_mastery,
            'mastery_variance': mastery_variance,
            'recent_accuracy': recent_accuracy,
            'total_questions': len(student.question_history),
            'batch_count': student.batch_count,
            'learning_trend': learning_trend,
            'ability_level': current_ability_level,
            'knowledge_connectivity': knowledge_connectivity
        }
    
    def _calculate_learning_trend(self, student: StudentModel) -> Dict:
        """计算学习趋势"""
        if len(student.vector_history) < 2:
            return {'trend': 'insufficient_data', 'momentum': 0.0}
        
        # 计算向量变化趋势
        recent_vectors = student.vector_history[-3:] if len(student.vector_history) >= 3 else student.vector_history
        
        # 计算学习动量（向量变化幅度）
        momentum = 0.0
        if len(recent_vectors) >= 2:
            for i in range(1, len(recent_vectors)):
                momentum += np.linalg.norm(recent_vectors[i] - recent_vectors[i-1])
            momentum /= (len(recent_vectors) - 1)
        
        # 计算掌握度变化趋势
        if len(student.question_history) >= 6:
            first_half = student.question_history[:len(student.question_history)//2]
            second_half = student.question_history[len(student.question_history)//2:]
            
            first_accuracy = sum(1 for q in first_half if q.get('correct', False)) / len(first_half)
            second_accuracy = sum(1 for q in second_half if q.get('correct', False)) / len(second_half)
            
            if second_accuracy > first_accuracy + 0.1:
                trend = 'improving'
            elif second_accuracy < first_accuracy - 0.1:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {'trend': trend, 'momentum': momentum}
    
    def _estimate_ability_level(self, student: StudentModel) -> str:
        """估算学生当前能力水平"""
        avg_mastery = sum(student.mastery_scores.values()) / len(student.mastery_scores) if student.mastery_scores else 0
        recent_accuracy = 0
        
        if len(student.question_history) >= 3:
            recent_questions = student.question_history[-5:]
            recent_accuracy = sum(1 for q in recent_questions if q.get('correct', False)) / len(recent_questions)
        
        # 综合掌握度和准确率判断能力水平
        combined_score = (avg_mastery + recent_accuracy) / 2
        
        if combined_score >= 0.8:
            return 'advanced'
        elif combined_score >= 0.6:
            return 'intermediate'
        elif combined_score >= 0.4:
            return 'beginner'
        else:
            return 'struggling'
    
    def _analyze_knowledge_connectivity(self, mastered_points: List[str], weak_points: List[Tuple[str, float]]) -> Dict:
        """分析知识点连通性"""
        connectivity_info = {
            'isolated_weak_points': [],
            'connected_weak_points': [],
            'expansion_candidates': []
        }
        
        # 分析薄弱知识点的连通性
        for weak_kp, score in weak_points:
            has_connection = False
            for mastered_kp in mastered_points:
                if weak_kp in self.embeddings and mastered_kp in self.embeddings:
                    similarity = cosine_similarity([self.embeddings[weak_kp]], 
                                                 [self.embeddings[mastered_kp]])[0][0]
                    if similarity > 0.3:  # 有强连接
                        has_connection = True
                        break
            
            if has_connection:
                connectivity_info['connected_weak_points'].append(weak_kp)
            else:
                connectivity_info['isolated_weak_points'].append(weak_kp)
        
        # 寻找拓展候选
        for mastered_kp in mastered_points:
            if mastered_kp in self.embeddings:
                for kp_id, embedding in self.embeddings.items():
                    if kp_id not in mastered_points and kp_id not in [wp[0] for wp in weak_points]:
                        similarity = cosine_similarity([self.embeddings[mastered_kp]], [embedding])[0][0]
                        if similarity > 0.4:
                            connectivity_info['expansion_candidates'].append((kp_id, similarity))
        
        # 按相似度排序拓展候选
        connectivity_info['expansion_candidates'].sort(key=lambda x: x[1], reverse=True)
        connectivity_info['expansion_candidates'] = connectivity_info['expansion_candidates'][:5]
        
        return connectivity_info
    
    def _determine_recommendation_strategy(self, learning_state: Dict) -> str:
        """根据学习状态确定推荐策略 - 智能化决策"""
        weak_count = len(learning_state['weak_points'])
        mastered_count = len(learning_state['mastered_points'])
        moderate_count = len(learning_state['moderate_points'])
        recent_accuracy = learning_state['recent_accuracy']
        avg_mastery = learning_state['avg_mastery']
        learning_trend = learning_state['learning_trend']
        ability_level = learning_state['ability_level']
        connectivity = learning_state['knowledge_connectivity']
        
        # 计算总知识点数
        total_kps = weak_count + mastered_count + moderate_count
        if total_kps == 0:
            return "balanced"  # 安全回退
        
        # 计算相对比例
        weak_ratio = weak_count / total_kps
        mastered_ratio = mastered_count / total_kps
        moderate_ratio = moderate_count / total_kps
        
        # 策略权重计算
        strategy_scores = {
            'gap_filling': 0.0,
            'consolidation': 0.0,
            'expansion': 0.0,
            'balanced': 0.2  # 基础权重
        }
        
        # 基于薄弱知识点比例
        if weak_ratio > 0.4:
            strategy_scores['gap_filling'] += 0.4
        elif weak_ratio > 0.2:
            strategy_scores['gap_filling'] += 0.2
        
        # 基于掌握知识点比例
        if mastered_ratio > 0.6:
            strategy_scores['expansion'] += 0.4
        elif mastered_ratio > 0.4:
            strategy_scores['expansion'] += 0.2
        
        # 基于中等掌握度比例
        if moderate_ratio > 0.4:
            strategy_scores['consolidation'] += 0.4
        elif moderate_ratio > 0.2:
            strategy_scores['consolidation'] += 0.2
        
        # 基于最近表现
        if recent_accuracy < 0.4:
            strategy_scores['gap_filling'] += 0.3
        elif recent_accuracy > 0.8:
            strategy_scores['expansion'] += 0.3
        else:
            strategy_scores['consolidation'] += 0.2
        
        # 基于学习趋势
        if learning_trend['trend'] == 'declining':
            strategy_scores['gap_filling'] += 0.2
            strategy_scores['consolidation'] += 0.1
        elif learning_trend['trend'] == 'improving':
            strategy_scores['expansion'] += 0.2
            strategy_scores['consolidation'] += 0.1
        
        # 基于能力水平
        if ability_level == 'struggling':
            strategy_scores['gap_filling'] += 0.3
        elif ability_level == 'advanced':
            strategy_scores['expansion'] += 0.3
        else:
            strategy_scores['consolidation'] += 0.2
        
        # 基于知识连通性
        if len(connectivity['isolated_weak_points']) > 2:
            strategy_scores['gap_filling'] += 0.2
        if len(connectivity['expansion_candidates']) > 3:
            strategy_scores['expansion'] += 0.2
        if len(connectivity['connected_weak_points']) > 1:
            strategy_scores['consolidation'] += 0.1
        
        # 选择得分最高的策略
        best_strategy = max(strategy_scores.items(), key=lambda x: x[1])[0]
        
        return best_strategy
    
    def _consolidation_recommend(self, student: StudentModel, num_questions: int, learning_state: Dict) -> List[Dict]:
        """巩固练习推荐：针对中等掌握度的知识点"""
        moderate_points = learning_state['moderate_points']
        mastered_points = learning_state['mastered_points']
        
        # 选择目标知识点（中等掌握度 + 部分已掌握）
        target_kps = [kp for kp, _ in moderate_points[:3]]  # 前3个中等掌握度知识点
        if mastered_points:
            target_kps.extend(mastered_points[:2])  # 加入2个已掌握知识点进行巩固
        
        return self._recommend_by_target_kps(student, target_kps, num_questions, 
                                           strategy_name="consolidation")
    
    def _gap_filling_recommend(self, student: StudentModel, num_questions: int, learning_state: Dict) -> List[Dict]:
        """查漏补缺推荐：针对薄弱知识点"""
        weak_points = learning_state['weak_points']
        mastered_points = learning_state['mastered_points']
        
        # 优先选择最薄弱的知识点，但要考虑与已掌握知识点的关联性
        target_kps = []
        
        # 选择与已掌握知识点相关的薄弱知识点
        if mastered_points and weak_points:
            related_weak_kps = self._find_related_weak_points(weak_points, mastered_points)
            target_kps.extend(related_weak_kps[:2])
        
        # 如果没有足够的相关薄弱知识点，直接选择最薄弱的
        if len(target_kps) < 2:
            remaining_weak = [kp for kp, _ in weak_points if kp not in target_kps]
            target_kps.extend(remaining_weak[:3-len(target_kps)])
        
        return self._recommend_by_target_kps(student, target_kps, num_questions,
                                           strategy_name="gap_filling")
    
    def _expansion_recommend(self, student: StudentModel, num_questions: int, learning_state: Dict) -> List[Dict]:
        """知识拓展推荐：基于已掌握知识点拓展新知识 - 增强版"""
        mastered_points = learning_state['mastered_points']
        connectivity = learning_state['knowledge_connectivity']
        
        if not mastered_points:
            return self._balanced_recommend(student, num_questions, learning_state)
        
        target_kps = []
        
        # 策略1: 利用连通性分析的拓展候选
        expansion_candidates = connectivity.get('expansion_candidates', [])
        if expansion_candidates:
            # 选择前3个最相似的候选
            target_kps.extend([kp for kp, _ in expansion_candidates[:3]])
        
        # 策略2: 基于向量推理的传统方法（作为补充）
        if len(target_kps) < 3:
            vector_based_candidates = []
            
            # 从多个已掌握知识点出发进行拓展
            top_mastered = sorted(mastered_points, 
                                key=lambda kp: student.get_mastery_level(kp), 
                                reverse=True)[:3]
            
            for mastered_kp in top_mastered:
                # 使用多种关系向量进行探索
                for relation_type in ["prerequisite", "similarity", "advanced"]:
                    relation_vector = self._get_enhanced_relation_vector(relation_type)
                    V_mastered = self.embeddings[mastered_kp]
                    V_target = V_mastered + relation_vector
                    
                    # 寻找未掌握的相关知识点
                    for kp_id, kp_embedding in self.embeddings.items():
                        if student.get_mastery_level(kp_id) < 0.3 and kp_id not in target_kps:  # 未掌握的知识点
                            similarity = cosine_similarity([V_target], [kp_embedding])[0][0]
                            mastery_weight = student.get_mastery_level(mastered_kp)
                            vector_based_candidates.append((kp_id, similarity * mastery_weight, mastered_kp, relation_type))
            
            # 去重并排序
            unique_vector_candidates = {}
            for kp_id, score, source_kp, relation_type in vector_based_candidates:
                if kp_id not in unique_vector_candidates or unique_vector_candidates[kp_id][0] < score:
                    unique_vector_candidates[kp_id] = (score, source_kp, relation_type)
            
            vector_sorted = sorted(unique_vector_candidates.keys(), 
                              key=lambda kp: unique_vector_candidates[kp][0], 
                              reverse=True)
            
            # 补充到目标知识点列表
            remaining_slots = 3 - len(target_kps)
            target_kps.extend([kp for kp in vector_sorted[:remaining_slots] if kp not in target_kps])
        
        return self._recommend_by_target_kps(student, target_kps, num_questions,
                                           strategy_name="expansion")
    
    def _get_enhanced_relation_vector(self, relation_type: str) -> np.ndarray:
        """获取增强的关系向量"""
        if relation_type == "prerequisite":
            # 先修关系：较保守的探索
            base_mean, base_std = 0.08, 0.12
        elif relation_type == "similarity":
            # 相似关系：中等探索
            base_mean, base_std = 0.12, 0.15
        elif relation_type == "advanced":
            # 进阶关系：较激进的探索
            base_mean, base_std = 0.18, 0.25
        else:
            base_mean, base_std = 0.12, 0.15
        
        # 添加随机性
        random_factor = np.random.uniform(0.85, 1.15)
        dynamic_mean = base_mean * random_factor
        dynamic_std = base_std * random_factor
        
        # 生成关系向量
        relation_vector = np.random.normal(dynamic_mean, dynamic_std, 50)
        return relation_vector / np.linalg.norm(relation_vector)
    
    def _balanced_recommend(self, student: StudentModel, num_questions: int, learning_state: Dict) -> List[Dict]:
        """平衡推荐：综合考虑各种知识点"""
        weak_points = learning_state['weak_points']
        moderate_points = learning_state['moderate_points']
        mastered_points = learning_state['mastered_points']
        
        # 平衡选择不同层次的知识点
        target_kps = []
        
        # 1个薄弱知识点（如果有）
        if weak_points:
            target_kps.append(weak_points[0][0])
        
        # 1-2个中等掌握度知识点
        if moderate_points:
            target_kps.extend([kp for kp, _ in moderate_points[:2]])
        
        # 1个已掌握知识点用于拓展
        if mastered_points and len(target_kps) < 3:
            target_kps.append(mastered_points[0])
        
        return self._recommend_by_target_kps(student, target_kps, num_questions,
                                           strategy_name="balanced")
    
    def _find_related_weak_points(self, weak_points: List[Tuple[str, float]], 
                                mastered_points: List[str]) -> List[str]:
        """找到与已掌握知识点相关的薄弱知识点"""
        related_weak = []
        
        for weak_kp, _ in weak_points:
            max_similarity = 0
            for mastered_kp in mastered_points:
                if weak_kp in self.embeddings and mastered_kp in self.embeddings:
                    similarity = cosine_similarity([self.embeddings[weak_kp]], 
                                                 [self.embeddings[mastered_kp]])[0][0]
                    max_similarity = max(max_similarity, similarity)
            
            if max_similarity > 0.3:  # 相似度阈值
                related_weak.append(weak_kp)
        
        return related_weak
    
    def _get_dynamic_relation_vector(self, strategy: str) -> np.ndarray:
        """获取动态关系向量，增加随机性"""
        # 根据策略调整基础参数
        if strategy == "gap_filling":
            base_mean, base_std = 0.05, 0.1  # 更保守的向量
        elif strategy == "expansion":
            base_mean, base_std = 0.15, 0.2  # 更激进的向量
        else:
            base_mean, base_std = 0.1, 0.15  # 默认参数
        
        # 添加随机抖动
        random_factor = np.random.uniform(0.8, 1.2)  # 随机因子
        dynamic_mean = base_mean * random_factor
        dynamic_std = base_std * random_factor
        
        # 生成动态关系向量
        relation_vector = np.random.normal(dynamic_mean, dynamic_std, 50)
        return relation_vector / np.linalg.norm(relation_vector)
    
    def _recommend_by_target_kps(self, student: StudentModel, target_kps: List[str], 
                               num_questions: int, strategy_name: str = "") -> List[Dict]:
        """根据目标知识点推荐题目 - 增强版"""
        if not target_kps:
            return []
        
        candidate_questions = []
        attempted = [ans['qid'] for ans in student.question_history]
        
        # 获取学生能力水平
        ability_level = self._estimate_ability_level(student)
        
        # 为每个目标知识点收集候选题目
        for target_kp in target_kps:
            kp_questions = []
            for q in self.questions:
                if q['qid'] in attempted:
                    continue
                
                if target_kp in q['knowledge_points']:
                    # 计算题目与目标知识点的关联度
                    kp_weight = q['knowledge_points'].get(target_kp, 0)
                    
                    # 计算与学生已掌握知识点的关联度
                    mastered_kps = student.get_mastered_knowledge_points(threshold=0.3)
                    mastered_overlap = sum(q['knowledge_points'].get(kp, 0) 
                                         for kp in mastered_kps) / len(mastered_kps) if mastered_kps else 0
                    
                    # 估算题目难度
                    difficulty_score = self._estimate_question_difficulty(q, student)
                    
                    # 计算难度适配度
                    difficulty_match = self._calculate_difficulty_match(difficulty_score, ability_level, strategy_name)
                    
                    kp_questions.append({
                        'question': q,
                        'target_kp': target_kp,
                        'kp_weight': kp_weight,
                        'mastered_overlap': mastered_overlap,
                        'difficulty_score': difficulty_score,
                        'difficulty_match': difficulty_match
                    })
            
            # 为每个知识点最多选择3道题
            kp_questions.sort(key=lambda x: (x['kp_weight'], x['difficulty_match'], x['mastered_overlap']), reverse=True)
            candidate_questions.extend(kp_questions[:3])
        
        # 综合评分
        scored_questions = []
        for cq in candidate_questions:
            question = cq['question']
            target_kp = cq['target_kp']
            kp_weight = cq['kp_weight']
            mastered_overlap = cq['mastered_overlap']
            difficulty_match = cq['difficulty_match']
            
            # 计算各项得分
            coverage_score = kp_weight
            relevance_score = mastered_overlap
            diversity_score = len(question['knowledge_points']) * 0.1
            adaptability_score = difficulty_match
            
            # 策略相关的权重调整 (加入难度适配维度)
            if strategy_name == "gap_filling":
                weights = [0.5, 0.2, 0.1, 0.2]  # 重视覆盖度和适配度
            elif strategy_name == "expansion":
                weights = [0.3, 0.2, 0.3, 0.2]  # 平衡各项指标
            elif strategy_name == "consolidation":
                weights = [0.4, 0.3, 0.1, 0.2]  # 重视关联性和适配度
            else:  # 平衡推荐
                weights = [0.4, 0.25, 0.15, 0.2]
            
            final_score = (
                weights[0] * coverage_score +
                weights[1] * relevance_score +
                weights[2] * diversity_score +
                weights[3] * adaptability_score
            )
            
            # 添加小量随机因子避免推荐过于固定
            random_factor = np.random.uniform(0.95, 1.05)
            final_score *= random_factor
            
            scored_questions.append((question, final_score, strategy_name))
        
        # 排序并返回前N个
        scored_questions.sort(key=lambda x: x[1], reverse=True)
        
        # 确保不超过请求数量
        final_questions = []
        for q, score, strategy in scored_questions[:num_questions]:
            # 记录推荐策略信息
            q_copy = q.copy()
            q_copy['recommendation_strategy'] = strategy
            q_copy['recommendation_score'] = score
            final_questions.append(q_copy)
        
        return final_questions
    
    def _estimate_question_difficulty(self, question: Dict, student: StudentModel) -> float:
        """估算题目难度"""
        # 基于知识点掌握度估算难度
        total_difficulty = 0.0
        total_weight = 0.0
        
        for kp_id, weight in question['knowledge_points'].items():
            mastery_level = student.get_mastery_level(kp_id)
            # 掌握度越低，题目对学生来说越难
            kp_difficulty = 1.0 - mastery_level
            total_difficulty += kp_difficulty * weight
            total_weight += weight
        
        if total_weight > 0:
            avg_difficulty = total_difficulty / total_weight
        else:
            avg_difficulty = 0.5  # 默认中等难度
        
        # 基于知识点数量调整难度（知识点越多通常越复杂）
        complexity_factor = min(len(question['knowledge_points']) / 3.0, 1.0)
        
        final_difficulty = (avg_difficulty + complexity_factor * 0.2)
        return min(final_difficulty, 1.0)
    
    def _calculate_difficulty_match(self, difficulty_score: float, ability_level: str, strategy_name: str) -> float:
        """计算难度适配度"""
        # 定义各能力水平的最佳难度范围
        optimal_difficulty_ranges = {
            'struggling': (0.2, 0.4),
            'beginner': (0.3, 0.5),
            'intermediate': (0.4, 0.7),
            'advanced': (0.6, 0.9)
        }
        
        # 根据策略调整难度偏好
        if strategy_name == "gap_filling":
            # 查漏补缺时倾向于较低难度
            adjustment = -0.1
        elif strategy_name == "expansion":
            # 知识拓展时倾向于较高难度
            adjustment = 0.1
        else:
            adjustment = 0.0
        
        # 获取最佳难度范围
        min_difficulty, max_difficulty = optimal_difficulty_ranges.get(ability_level, (0.4, 0.7))
        min_difficulty = max(0.0, min_difficulty + adjustment)
        max_difficulty = min(1.0, max_difficulty + adjustment)
        
        # 计算适配度
        if min_difficulty <= difficulty_score <= max_difficulty:
            # 在最佳范围内，越接近中心点越好
            center = (min_difficulty + max_difficulty) / 2
            distance_from_center = abs(difficulty_score - center)
            max_distance = (max_difficulty - min_difficulty) / 2
            match_score = 1.0 - (distance_from_center / max_distance) if max_distance > 0 else 1.0
        else:
            # 超出最佳范围，根据距离计算惩罚
            if difficulty_score < min_difficulty:
                distance = min_difficulty - difficulty_score
            else:
                distance = difficulty_score - max_difficulty
            match_score = max(0.0, 1.0 - distance * 2)  # 距离越远，适配度越低
        
        return match_score
    
    def evaluate_recommendation_quality(self, student: StudentModel, recommendations: List[Dict]) -> Dict:
        """评估推荐质量"""
        if not recommendations:
            return {"quality_score": 0.0, "details": "无推荐题目"}
        
        quality_metrics = {
            "coverage_diversity": 0.0,    # 知识点覆盖多样性
            "difficulty_appropriateness": 0.0,  # 难度适宜性
            "learning_progression": 0.0,  # 学习进阶性
            "personalization": 0.0        # 个性化程度
        }
        
        # 1. 知识点覆盖多样性
        all_kps = set()
        for rec in recommendations:
            all_kps.update(rec['knowledge_points'].keys())
        
        weak_kps = set([kp for kp, _ in student.get_weak_knowledge_points()])
        moderate_kps = set([kp for kp, score in student.mastery_scores.items() if 0.3 <= score < 0.5])
        
        coverage_score = 0.0
        if weak_kps:
            weak_coverage = len(all_kps & weak_kps) / len(weak_kps)
            coverage_score += weak_coverage * 0.6
        if moderate_kps:
            moderate_coverage = len(all_kps & moderate_kps) / len(moderate_kps)
            coverage_score += moderate_coverage * 0.4
        
        quality_metrics["coverage_diversity"] = min(coverage_score, 1.0)
        
        # 2. 难度适宜性
        ability_level = self._estimate_ability_level(student)
        difficulty_scores = []
        
        for rec in recommendations:
            difficulty = self._estimate_question_difficulty(rec, student)
            appropriateness = self._calculate_difficulty_match(difficulty, ability_level, 
                                                             rec.get('recommendation_strategy', ''))
            difficulty_scores.append(appropriateness)
        
        quality_metrics["difficulty_appropriateness"] = sum(difficulty_scores) / len(difficulty_scores)
        
        # 3. 学习进阶性（推荐题目是否有合理的学习路径）
        progression_score = 0.0
        if len(recommendations) > 1:
            # 检查推荐题目间的知识关联性
            connections = 0
            total_pairs = 0
            
            for i in range(len(recommendations)):
                for j in range(i + 1, len(recommendations)):
                    total_pairs += 1
                    # 计算两题目知识点的交集
                    kps1 = set(recommendations[i]['knowledge_points'].keys())
                    kps2 = set(recommendations[j]['knowledge_points'].keys())
                    if kps1 & kps2:  # 有共同知识点
                        connections += 1
            
            if total_pairs > 0:
                progression_score = connections / total_pairs
        
        quality_metrics["learning_progression"] = progression_score
        
        # 4. 个性化程度
        personalization_score = 0.0
        
        # 检查推荐是否针对学生的薄弱环节
        student_weak_areas = set([kp for kp, _ in student.get_weak_knowledge_points(threshold=0.4)])
        if student_weak_areas:
            weak_targeted = sum(1 for rec in recommendations 
                              if set(rec['knowledge_points'].keys()) & student_weak_areas)
            personalization_score += (weak_targeted / len(recommendations)) * 0.5
        
        # 检查推荐策略的多样性
        strategies = set([rec.get('recommendation_strategy', 'unknown') for rec in recommendations])
        strategy_diversity = len(strategies) / 4.0  # 假设最多4种策略
        personalization_score += strategy_diversity * 0.3
        
        # 检查是否避免了学生已经很熟练的知识点
        mastered_kps = set(student.get_mastered_knowledge_points(threshold=0.8))
        if mastered_kps:
            non_mastered_focus = sum(1 for rec in recommendations 
                                   if not (set(rec['knowledge_points'].keys()) <= mastered_kps))
            personalization_score += (non_mastered_focus / len(recommendations)) * 0.2
        
        quality_metrics["personalization"] = min(personalization_score, 1.0)
        
        # 计算综合质量分数
        weights = [0.3, 0.3, 0.2, 0.2]  # 各维度权重
        overall_score = sum(w * score for w, score in zip(weights, quality_metrics.values()))
        
        return {
            "quality_score": overall_score,
            "details": quality_metrics,
            "recommendations_count": len(recommendations),
            "coverage_knowledge_points": len(all_kps)
        }

class KnowledgeGraphRecommendationEngine:
    """知识图谱推荐引擎 - 主要接口类"""
    
    def __init__(self, config_path: str = None):
        """初始化推荐引擎"""
        # 默认配置
        self.embeddings_path = "embeddings.csv"
        self.knowledge_graph_path = "knowledge_graph.csv" 
        self.question_bank_path = "question_bank.json"
        self.node_names = "formatted_nodes.csv"
        
        # 加载配置
        if config_path:
            print("加载配置文件:", config_path)
            self._load_config(config_path)
        
        # 初始化推荐系统
        self.recommender = RecommendationSystem(
            self.embeddings_path,
            self.knowledge_graph_path,
            self.question_bank_path,
            self.node_names
        )
        
        # 存储学生模型
        self.students = {}
    
    def _load_config(self, config_path: str) -> None:
        """加载配置文件"""
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print("读取配置文件内容")
        
            self.embeddings_path = config.get("paths", {}).get("embeddings_path", "无描述")
            print("使用的embeddings_path:", self.embeddings_path)
            self.knowledge_graph_path = config.get("paths", {}).get('knowledge_graph_path', "无描述")
            print("使用的knowledge_graph_path:", self.knowledge_graph_path)
            self.question_bank_path = config.get("paths", {}).get('question_bank_path', "无描述")
            print("使用的question_bank_path:", self.question_bank_path)
    
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
            kp_name = self.recommender._get_node_name(kp)
            if score < 0.1:
                recommendations.append(f"🔴 {kp_name} 掌握度极低({score:.2f})，建议重点学习基础概念")
            elif score < 0.2:
                recommendations.append(f"🟡 {kp_name} 掌握度较低({score:.2f})，需要加强练习")
            else:
                recommendations.append(f"🟠 {kp_name} 掌握度一般({score:.2f})，可以适量练习巩固")
        
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
