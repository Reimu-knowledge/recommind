# 推荐算法优化方案

## 🔍 当前算法分析

### 现有推荐流程
1. **学生建模**: 基于50维向量表示学生知识状态
2. **向量推理**: `V_target = V_mastered + V_prerequisite` 
3. **候选筛选**: 找到与目标向量相似的未掌握知识点
4. **多维评分**: 覆盖度(40%) + 相关性(30%) + 难度(20%) + 多样性(10%)
5. **题目推荐**: 返回综合评分最高的题目

### 算法优势
- 🎯 基于向量推理，有理论基础
- 📊 多维评分机制，考虑多个因素
- 🔄 动态学习更新，适应学生进展
- 🚀 冷启动处理，新用户友好

## 🚀 优化策略

### 1. 智能难度调节
**现状**: 固定目标难度0.6，难度评分简单线性
**优化**: 根据学生水平动态调整难度

```python
def adaptive_difficulty_scoring(self, student_model, question_difficulty):
    # 计算学生当前平均掌握度
    avg_mastery = np.mean(list(student_model.mastery_scores.values()))
    
    # 动态调整目标难度
    if avg_mastery < 0.3:      # 初学者
        target_difficulty = 0.4
    elif avg_mastery < 0.6:    # 中等水平
        target_difficulty = 0.6  
    else:                      # 高水平
        target_difficulty = 0.8
    
    # 考虑学习曲线，稍微偏向更有挑战性的题目
    challenge_factor = 1.1
    target_difficulty = min(1.0, target_difficulty * challenge_factor)
    
    # 使用高斯分布而不是线性距离
    difficulty_score = np.exp(-((question_difficulty - target_difficulty) ** 2) / (2 * 0.1 ** 2))
    return difficulty_score
```

### 2. 学习路径优化
**现状**: 只考虑单步前置关系
**优化**: 引入学习路径规划

```python
def compute_learning_path_score(self, student_model, target_kp):
    # 计算到目标知识点的最短学习路径
    path_length = self._find_shortest_learning_path(
        student_model.get_mastered_knowledge_points(), 
        target_kp
    )
    
    # 路径越短，优先级越高
    path_score = 1.0 / (1.0 + path_length * 0.2)
    return path_score

def _find_shortest_learning_path(self, mastered_kps, target_kp):
    # 使用BFS找到从已掌握知识点到目标知识点的最短路径
    # 这里需要知识图谱的拓扑结构
    return self._bfs_knowledge_graph(mastered_kps, target_kp)
```

### 3. 个性化权重调整
**现状**: 固定权重配置
**优化**: 根据学生特点动态调整权重

```python
def adaptive_scoring_weights(self, student_model):
    # 分析学生的学习模式
    answer_history = student_model.question_history
    
    if len(answer_history) < 5:
        # 新学生：重视基础覆盖
        return {'coverage': 0.5, 'relevance': 0.3, 'difficulty': 0.15, 'diversity': 0.05}
    
    # 计算学生的正确率
    accuracy = sum(1 for ans in answer_history if ans['correct']) / len(answer_history)
    
    if accuracy > 0.8:
        # 高水平学生：重视挑战性和多样性
        return {'coverage': 0.3, 'relevance': 0.25, 'difficulty': 0.3, 'diversity': 0.15}
    elif accuracy < 0.5:
        # 需要巩固基础：重视相关性和适当难度
        return {'coverage': 0.4, 'relevance': 0.4, 'difficulty': 0.15, 'diversity': 0.05}
    else:
        # 中等水平：使用默认权重
        return {'coverage': 0.4, 'relevance': 0.3, 'difficulty': 0.2, 'diversity': 0.1}
```

### 4. 遗忘曲线建模
**现状**: 掌握度只增不减
**优化**: 引入遗忘机制

```python
def apply_forgetting_curve(self, student_model):
    current_time = time.time()
    
    for kp_id, mastery_score in student_model.mastery_scores.items():
        # 找到该知识点最后一次练习时间
        last_practice = self._get_last_practice_time(student_model, kp_id)
        
        if last_practice:
            # 计算时间衰减（艾宾浩斯遗忘曲线）
            days_elapsed = (current_time - last_practice) / (24 * 3600)
            
            # 遗忘函数: R(t) = e^(-t/S), S是记忆强度
            memory_strength = mastery_score * 5  # 掌握度越高，记忆强度越大
            retention_rate = np.exp(-days_elapsed / memory_strength)
            
            # 应用遗忘衰减
            new_mastery = mastery_score * retention_rate
            student_model.mastery_scores[kp_id] = max(0.0, new_mastery)
```

### 5. 多目标优化
**现状**: 简单线性加权
**优化**: 使用帕累托最优

```python
def pareto_optimal_selection(self, candidate_questions, weights):
    # 计算每个题目在各个维度的得分
    scores_matrix = []
    for cq in candidate_questions:
        scores = [
            self._coverage_score(cq),
            self._relevance_score(cq), 
            self._difficulty_score(cq),
            self._diversity_score(cq)
        ]
        scores_matrix.append(scores)
    
    scores_matrix = np.array(scores_matrix)
    
    # 找到帕累托前沿
    pareto_front = self._find_pareto_front(scores_matrix)
    
    # 在帕累托前沿中使用权重选择
    weighted_scores = np.dot(scores_matrix[pareto_front], list(weights.values()))
    best_indices = pareto_front[np.argsort(weighted_scores)[::-1]]
    
    return [candidate_questions[i] for i in best_indices]
```

### 6. 强化学习优化
**现状**: 静态推荐策略
**优化**: 根据反馈动态调整

```python
class RLRecommendationOptimizer:
    def __init__(self):
        self.action_values = {}  # Q值表
        self.epsilon = 0.1       # 探索率
        
    def select_action(self, state, available_actions):
        state_key = self._state_to_key(state)
        
        if np.random.random() < self.epsilon:
            # 探索：随机选择
            return np.random.choice(available_actions)
        else:
            # 利用：选择Q值最高的动作
            q_values = [self.action_values.get((state_key, action), 0.0) 
                       for action in available_actions]
            return available_actions[np.argmax(q_values)]
    
    def update_q_value(self, state, action, reward, next_state):
        # Q-learning更新
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # 计算TD误差并更新Q值
        old_q = self.action_values.get((state_key, action), 0.0)
        max_next_q = max([self.action_values.get((next_state_key, a), 0.0) 
                         for a in self._get_available_actions(next_state)], default=0.0)
        
        alpha = 0.1  # 学习率
        gamma = 0.9  # 折扣因子
        
        new_q = old_q + alpha * (reward + gamma * max_next_q - old_q)
        self.action_values[(state_key, action)] = new_q
```

## 📊 实施优先级

### 🔥 高优先级 (立即实施)
1. **智能难度调节**: 显著提升题目适配性
2. **个性化权重**: 提高推荐精度
3. **遗忘曲线**: 更真实的学习建模

### 🔧 中优先级 (短期规划)
4. **学习路径优化**: 需要完善知识图谱结构
5. **多目标优化**: 数学模型较复杂

### 🚀 低优先级 (长期规划) 
6. **强化学习**: 需要大量用户反馈数据

## 💡 快速改进建议

立即可以实施的优化：

```python
# 1. 添加智能难度调节到现有代码
def enhanced_difficulty_scoring(self, student_model, question_difficulty):
    avg_mastery = np.mean(list(student_model.mastery_scores.values()))
    target_difficulty = 0.4 + avg_mastery * 0.4  # 动态范围0.4-0.8
    return np.exp(-((question_difficulty - target_difficulty) ** 2) / 0.02)

# 2. 添加学习进度考虑
def progress_aware_relevance(self, student_model, kp_similarity):
    # 考虑学生的学习速度，调整相关性权重
    recent_progress = self._calculate_recent_progress(student_model)
    progress_multiplier = 1.0 + recent_progress * 0.2
    return kp_similarity * progress_multiplier

# 3. 添加时间衰减机制
def time_aware_mastery(self, student_model):
    # 简化版遗忘曲线
    for kp_id in student_model.mastery_scores:
        days_since_practice = self._get_days_since_practice(student_model, kp_id)
        if days_since_practice > 7:  # 一周没练习开始遗忘
            decay_factor = 0.95 ** (days_since_practice - 7)
            student_model.mastery_scores[kp_id] *= decay_factor
```

这些优化将显著提升推荐系统的智能化程度和个性化效果！
