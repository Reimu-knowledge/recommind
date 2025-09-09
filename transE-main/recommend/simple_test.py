#!/usr/bin/env python3
"""
简化测试：直接在代码中定义题库，测试学生建模和推荐系统
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import random
import json
import pandas as pd

# 直接在json中读取题库
with open("question_bank.json", "r", encoding="utf-8") as f:
    TEST_QUESTIONS = json.load(f)['questions']

class SimpleStudentModel:
    """简化的学生模型"""
    
    def __init__(self, student_id, initial_mastery=None, embedding_dim=50):
        self.student_id = student_id
        self.embedding_dim = embedding_dim
        
        # 初始化掌握度（可以从外部设置）
        if initial_mastery is None:
            # 默认初始掌握度：对基础知识点有少量掌握
            self.mastery_scores = {
                'K1': 0.1,  # 集合运算
                'K2': 0.1,  # 关系映射
                'K3': 0.05, # 图基本概念
            }
        else:
            self.mastery_scores = initial_mastery.copy()
        
        # 从掌握度计算初始学生向量
        self.vector = None  # 将在设置嵌入后计算
        self.question_history = []
        self.batch_count = 0
        self.vector_history = []
    
    def initialize_vector_from_mastery(self, embeddings):
        """从知识点掌握度计算初始学生向量"""
        print(f"\n=== 初始化学生向量 ===")
        print(f"初始掌握度: {self.mastery_scores}")
        
        # 方法1: 加权平均法
        # V_student = Σ(mastery_score_i × V_knowledge_point_i) / Σ(mastery_score_i)
        weighted_vector = np.zeros(self.embedding_dim)
        total_weight = 0
        
        for kp_id, mastery_score in self.mastery_scores.items():
            if kp_id in embeddings and mastery_score > 0:
                weighted_vector += mastery_score * embeddings[kp_id]
                total_weight += mastery_score
                print(f"  {kp_id}: 掌握度={mastery_score:.3f}")
        
        if total_weight > 0:
            self.vector = weighted_vector / total_weight
        else:
            # 如果没有任何掌握度，使用随机小向量
            self.vector = np.random.normal(0, 0.1, self.embedding_dim)
        
        # 归一化向量
        if np.linalg.norm(self.vector) > 0:
            self.vector = self.vector / np.linalg.norm(self.vector)
        
        self.vector_history = [self.vector.copy()]
        
        print(f"初始学生向量模长: {np.linalg.norm(self.vector):.4f}")
        print(f"向量前5维: {self.vector[:5]}")
        
        # 验证初始向量与已掌握知识点的相似度
        print("初始向量与知识点相似度:")
        for kp_id, mastery in self.mastery_scores.items():
            if kp_id in embeddings:
                sim = cosine_similarity([self.vector], [embeddings[kp_id]])[0][0]
                print(f"  {kp_id} (掌握度={mastery:.3f}): 相似度={sim:.4f}")
    
    def update_from_batch(self, batch_answers, embeddings, alpha=0.7):
        # 计算批次向量
        batch_vector = self._compute_batch_vector(batch_answers, embeddings)
        
        # 更新学生向量
        if self.batch_count == 0:
            self.vector = batch_vector
        else:
            self.vector = alpha * self.vector + (1 - alpha) * batch_vector
        
        # 归一化
        if np.linalg.norm(self.vector) > 0:
            self.vector = self.vector / np.linalg.norm(self.vector)
        
        # 更新掌握度
        self._update_mastery_scores(batch_answers)
        
        # 记录历史
        self.question_history.extend(batch_answers)
        self.vector_history.append(self.vector.copy())
        self.batch_count += 1
        
        print(f"学生 {self.student_id} 完成第 {self.batch_count} 批次")
        print(f"  向量模长: {np.linalg.norm(self.vector):.4f}")
        involved_kps = set().union(*[ans['knowledge_points'].keys() for ans in batch_answers])
        print(f"  涉及知识点: {involved_kps}")
    
    def _compute_batch_vector(self, batch_answers, embeddings):
        """计算单批次的学习向量 - 只有正反馈"""
        batch_vector = np.zeros(len(list(embeddings.values())[0]))
        
        for answer in batch_answers:
            for kp_id, weight in answer["knowledge_points"].items():
                if kp_id in embeddings:
                    kp_embedding = embeddings[kp_id]
                    if answer["correct"]:
                        # 答对：向知识点方向强移动
                        learning_strength = 1.0 * weight
                    else:
                        # 答错：向知识点方向弱移动（仍然学到了一些）
                        learning_strength = 0.3 * weight
                    
                    batch_vector += learning_strength * kp_embedding
        
        if len(batch_answers) > 0:
            batch_vector /= len(batch_answers)
        
        return batch_vector
    
    def _update_mastery_scores(self, batch_answers):
        """更新知识点掌握度数值 - 只有正反馈"""
        for answer in batch_answers:
            for kp_id, weight in answer["knowledge_points"].items():
                if kp_id not in self.mastery_scores:
                    self.mastery_scores[kp_id] = 0.0
                
                if answer["correct"]:
                    # 答对：较大的正反馈
                    delta = 0.3 * weight
                    self.mastery_scores[kp_id] = min(1.0, self.mastery_scores[kp_id] + delta)
                else:
                    # 答错：较小的正反馈（接触了知识点，有一定学习效果）
                    delta = 0.1 * weight
                    self.mastery_scores[kp_id] = min(1.0, self.mastery_scores[kp_id] + delta)
    
    def get_mastered_knowledge_points(self, threshold=0.5):
        return [kp for kp, score in self.mastery_scores.items() if score >= threshold]
    
    def get_mastery_level(self, kp_id):
        return self.mastery_scores.get(kp_id, 0.0)

class SimpleRecommender:
    """简化的推荐系统"""
    
    def __init__(self, embeddings_path, relation_vector_method="simulated"):
        self.embeddings = self._load_embeddings(embeddings_path)
        self.questions = TEST_QUESTIONS
        
        # 关系向量获取 - 提供多种方法和接口
        self.relation_embeddings = self._initialize_relation_vectors(relation_vector_method)
        
        print(f"简化推荐系统初始化完成:")
        print(f"  知识点数量: {len(self.embeddings)}")
        print(f"  题目数量: {len(self.questions)}")
        print(f"  关系向量方法: {relation_vector_method}")
    
    def _initialize_relation_vectors(self, method="simulated"):
        """初始化关系向量 - 提供多种获取方法"""
        relation_embeddings = {}
        
        if method == "simulated":
            # 方法1: 基于先验知识的模拟
            print("使用模拟关系向量...")
            np.random.seed(42)
            
            # 前置关系：应该指向"更高层次"的方向
            # 基于知识图谱的层次结构，前置关系向量应该有向性
            prerequisite_vector = np.random.normal(0.1, 0.15, 50)  # 稍微正向偏移
            relation_embeddings["is_prerequisite_for"] = prerequisite_vector / np.linalg.norm(prerequisite_vector)
            
            # 相关关系：小的随机扰动，表示知识点间的相关性
            related_vector = np.random.normal(0, 0.05, 50)  # 接近零向量
            relation_embeddings["is_related_to"] = related_vector / np.linalg.norm(related_vector)
            
        elif method == "knowledge_graph_based":
            # 方法2: 基于知识图谱结构计算（未来实现）
            print("使用基于知识图谱的关系向量...")
            relation_embeddings = self._compute_graph_based_relations()
            
        elif method == "transE_trained":
            # 方法3: 从训练好的TransE模型加载（接口预留）
            print("从TransE模型加载关系向量...")
            relation_embeddings = self._load_transE_relations()
            
        else:
            raise ValueError(f"Unknown relation vector method: {method}")
        
        return relation_embeddings
    
    def _compute_graph_based_relations(self):
        """基于知识图谱结构计算关系向量（示例实现）"""
        # TODO: 实现基于图结构的关系向量计算
        # 例如：分析前置关系的方向性，计算平均向量差等
        return {
            "is_prerequisite_for": np.random.normal(0.1, 0.15, 50),
            "is_related_to": np.random.normal(0, 0.05, 50)
        }
    
    def _load_transE_relations(self):
        """从TransE模型加载关系向量（接口预留）"""
        # TODO: 实现从实际TransE模型文件加载关系向量
        # 例如：从 relation_embeddings.npy 或模型checkpoint加载
        print("Warning: TransE关系向量加载未实现，使用模拟向量")
        return {
            "is_prerequisite_for": np.random.normal(0.1, 0.15, 50),
            "is_related_to": np.random.normal(0, 0.05, 50)
        }
    
    def set_relation_vectors(self, relation_embeddings):
        """外部接口：设置关系向量"""
        self.relation_embeddings = relation_embeddings
        print("关系向量已更新")
    
    def _load_embeddings(self, path):
        df = pd.read_csv(path)
        embeddings = {}
        for _, row in df.iterrows():
            kp_id = row['kp_id']
            vector = row.iloc[1:].values.astype(float)
            embeddings[kp_id] = vector
        return embeddings
    
    def recommend_questions(self, student_model, num_questions=3):
        print(f"\n=== 向量推荐算法 ===")
        
        mastered_kps = student_model.get_mastered_knowledge_points(threshold=0.1)
        
        if not mastered_kps:
            # 冷启动：推荐基础题目
            print("冷启动：推荐基础知识点")
            basic_questions = [q['qid'] for q in self.questions
                             if any(kp in ['K1', 'K2', 'K3'] for kp in q['knowledge_points'].keys())]
            return basic_questions[:num_questions]
        
        # 选择掌握度最高的知识点作为基准
        best_mastered = max(mastered_kps, key=lambda kp: student_model.get_mastery_level(kp))
        print(f"基准知识点: {best_mastered} (掌握度: {student_model.get_mastery_level(best_mastered):.3f})")
        
        # 向量推理：V_target = V_mastered + V_prerequisite
        V_mastered = self.embeddings[best_mastered]
        V_target = V_mastered + self.relation_embeddings["is_prerequisite_for"]
        
        print(f"目标向量计算: V_{best_mastered} + V_prerequisite")
        
        # 找到最相似的未掌握知识点
        candidates = []
        for kp_id, kp_embedding in self.embeddings.items():
            if student_model.get_mastery_level(kp_id) < 0.5:
                similarity = cosine_similarity([V_target], [kp_embedding])[0][0]
                candidates.append((kp_id, similarity))
        
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        print("推荐知识点排序:")
        for i, (kp_id, sim) in enumerate(candidates[:10]):
            mastery = student_model.get_mastery_level(kp_id)
            print(f"  {i+1}. {kp_id}: 相似度={sim:.4f}, 掌握度={mastery:.3f}")
        
        # 为推荐知识点找题目 - 改进逻辑
        if candidates:
            # 收集候选题目：遍历候选知识点直到有足够题目
            candidate_questions = []
            attempted_questions = [ans['qid'] for ans in student_model.question_history]
            
            target_question_count = 8  # 目标收集8道候选题目
            
            for kp_id, kp_similarity in candidates:
                if len(candidate_questions) >= target_question_count:
                    break
                    
                # 找涉及该知识点的题目
                for q in self.questions:
                    if len(candidate_questions) >= target_question_count:
                        break
                        
                    # 跳过已做过的题目
                    if q['qid'] in attempted_questions:
                        continue
                    
                    # 检查是否涉及当前知识点
                    if kp_id in q['knowledge_points']:
                        # 避免重复添加同一题目
                        if not any(cq['qid'] == q['qid'] for cq in candidate_questions):
                            candidate_questions.append({
                                'qid': q['qid'],
                                'question': q,
                                'target_kp': kp_id,
                                'kp_similarity': kp_similarity
                            })
            
            print(f"收集到 {len(candidate_questions)} 道候选题目")
            
            # 综合评分：知识点覆盖度 + 相关程度 + 难度适配度
            scored_questions = []
            
            for cq in candidate_questions:
                question = cq['question']
                target_kp = cq['target_kp']
                kp_similarity = cq['kp_similarity']
                
                # 1. 知识点覆盖程度（该题目对目标知识点的权重）
                coverage_score = question['knowledge_points'].get(target_kp, 0)
                
                # 2. 相关程度（目标知识点与学生当前向量的相似度）
                relevance_score = kp_similarity
                
                # 3. 难度适配度（偏好中等难度，可根据学生水平调整）
                target_difficulty = 0.6  # 目标难度
                difficulty_score = 1 - abs(question.get('difficulty', 0.5) - target_difficulty)
                
                # 4. 知识点多样性（涉及多个知识点的题目可能更有价值）
                diversity_score = len(question['knowledge_points']) * 0.1  # 轻微加分
                
                # 综合评分（可调整权重）
                final_score = (
                    0.4 * coverage_score +      # 40% 覆盖程度
                    0.3 * relevance_score +     # 30% 相关程度  
                    0.2 * difficulty_score +    # 20% 难度适配
                    0.1 * diversity_score       # 10% 多样性
                )
                
                scored_questions.append((
                    cq['qid'], 
                    final_score, 
                    {
                        'coverage': coverage_score,
                        'relevance': relevance_score, 
                        'difficulty': difficulty_score,
                        'diversity': diversity_score,
                        'target_kp': target_kp
                    }
                ))
            
            # 按综合评分排序
            scored_questions.sort(key=lambda x: x[1], reverse=True)
            
            print("题目综合评分排序:")
            for i, (qid, score, details) in enumerate(scored_questions[:6]):
                print(f"  {i+1}. {qid}: 综合={score:.3f} (覆盖={details['coverage']:.2f}, "
                      f"相关={details['relevance']:.2f}, 难度={details['difficulty']:.2f}, "
                      f"多样={details['diversity']:.2f}, 目标={details['target_kp']})")
            
            # 推荐前3道题目
            recommended = [qid for qid, _, _ in scored_questions[:num_questions]]
            print(f"\n最终推荐题目: {recommended}")
            return recommended
        
        return []

def simulate_learning():
    """运行学习模拟"""
    
    # 初始化推荐系统
    recommender = SimpleRecommender('/home/dzz/KGsystem/transE/recommend/embeddings.csv')
    
    # 设置学生初始掌握度（可以从用户输入或测试获取）
    initial_mastery = {
        'K1': 0.2,   # 集合运算：有一定基础
        'K2': 0.15,  # 关系映射：有少量了解
        'K3': 0.1,   # 图基本概念：刚接触
        'K8': 0.05,  # 度的概念：很少了解
    }
    
    # 创建学生，传入初始掌握度
    student = SimpleStudentModel("test_student", initial_mastery=initial_mastery)
    
    # 基于掌握度计算初始向量
    student.initialize_vector_from_mastery(recommender.embeddings)
    
    print(f"\n{'='*60}")
    print("开始学习模拟")
    print(f"{'='*60}")

    for round_num in range(1, 6):
        print(f"\n【第 {round_num} 轮学习】")
        
        # 推荐题目
        recommended_qids = recommender.recommend_questions(student)
        
        if not recommended_qids:
            print("无推荐题目，结束学习")
            break
        
        # 模拟答题
        print(f"\n推荐题目:")
        batch_answers = []
        
        for i, qid in enumerate(recommended_qids):
            question = recommender.questions[int(qid[1:])-1]
            print(f"  {i+1}. {qid}: {question['content']}")
            print(f"     选项: {question['options']}")
            print(f"     涉及知识点: {question['knowledge_points']}")
            
            # 模拟答题结果
            avg_mastery = np.mean([student.get_mastery_level(kp) for kp in question['knowledge_points'].keys()])
            success_prob = 0.5 + 0.3 * avg_mastery
            is_correct = random.random() < success_prob
            
            batch_answers.append({
                "qid": qid,
                "correct": is_correct,
                "knowledge_points": question['knowledge_points']
            })
            
            result = "✓ 正确" if is_correct else "✗ 错误"
            print(f"     答题结果: {result}")
        
        # 更新学生模型
        student.update_from_batch(batch_answers, recommender.embeddings)
        
        # 显示当前状态
        print(f"\n当前掌握情况:")
        mastered = student.get_mastered_knowledge_points()
        print(f"  已掌握知识点: {mastered}")
        
        mastery_items = [(kp, score) for kp, score in student.mastery_scores.items()]
        mastery_items.sort(key=lambda x: x[1], reverse=True)
        print(f"  掌握度排序: {mastery_items[:5]}")
        print(f"  学生向量模长: {np.linalg.norm(student.vector):.4f}")
    
    return student, recommender

if __name__ == "__main__":
    final_student, recommender = simulate_learning()
    
    print(f"\n{'='*60}")
    print("学习结果分析")
    print(f"{'='*60}")
    print(f"完成学习批次: {final_student.batch_count}")
    print(f"累计答题数量: {len(final_student.question_history)}")
    print(f"知识点掌握数量: {len(final_student.get_mastered_knowledge_points())}")
    
    all_masteries = list(final_student.mastery_scores.values())
    if all_masteries:
        print(f"掌握度统计: 平均={np.mean(all_masteries):.3f}, 标准差={np.std(all_masteries):.3f}")
        print(f"最终掌握度分布:")
        for kp, score in sorted(final_student.mastery_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  {kp}: {score:.3f}")
