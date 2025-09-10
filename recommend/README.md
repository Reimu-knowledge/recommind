# 基于知识图谱嵌入的智能教育推荐系统

## 🎓 项目概述

本项目实现了一个基于TransE知识图谱嵌入的智能教育推荐系统，专注于离散数学/图论领域的个性化自适应学习。系统集成了先进的向量化学习建模、智能推荐算法和完整的教学辅助功能。

> 由于文档较多，请优先阅读[DOC_INDEX.md](DOC_INDEX.md)

### 🌟 核心特色

1. **🧠 向量化学生建模**：将学生知识状态表示为50维语义向量
2. **🎯 智能推荐算法**：基于 `V_target = V_mastered + V_prerequisite` 的向量推理
3. **📊 实时学习分析**：自动判分、薄弱知识点诊断、学习轨迹追踪
4. **🔗 语义化知识图谱**：26个知识点的高质量嵌入向量
5. **⚡ 完整API接口**：为前端集成提供标准化服务
6. **💾 数据持久化支持**：完整的B/S架构数据存储和恢复方案
7. **🔄 个性化学习优化**：支持遗忘曲线建模和个性化权重调整

## 🚀 快速开始

### 环境配置
```bash
# 激活conda环境
conda activate dzz

# 确保依赖包已安装
pip install numpy pandas scikit-learn
```

### 运行方式

#### 🎮 交互式学习（推荐用于体验）
```bash
python start.py interactive
```

#### 🔥 演示模式（快速了解系统能力）
```bash
python start.py demo
```

#### 💻 API模式（前端集成）
```python
from start import EducationRecommendationAPI
api = EducationRecommendationAPI()
```

## 🏗️ 系统架构

### 核心组件

```
recommend/
├── start.py                      # 🚀 主启动文件，API接口
├── simple_system.py              # 🧠 核心推荐系统逻辑
├── api_example.py               # 📖 API使用示例
├── api_response_examples.py     # 📋 返回值格式示例
├── persistence_demo.py          # 💾 数据持久化演示
├── test_persistence_compatibility.py # 🧪 持久化兼容性测试
├── embeddings.csv               # 🔗 50维语义嵌入向量
├── knowledge_graph.csv          # 📊 知识图谱关系数据
├── question_bank.json           # 📚 题库（25道题目）
├── config.json                  # ⚙️ 系统配置文件
├── README_API.md               # 📖 完整API文档
├── API_QUICK_REFERENCE.md      # ⚡ API快速参考
├── PERSISTENCE_API_REFERENCE.md # 💾 数据持久化API文档
├── OPTIMIZATION_REPORT.md      # 🚀 推荐算法优化报告
└── README.md                   # 📄 本文档
```

### 数据结构

#### 📊 知识图谱 (`knowledge_graph.csv`)
- **26个知识点**：K1-K26，涵盖离散数学和图论核心概念
- **关系类型**：`is_prerequisite_for`, `is_related_to`
- **学习路径**：K1(集合运算) → K2(关系映射) → K3(图基本概念) → K8(算法概念)

#### 📚 智能题库 (`question_bank.json`)
- **25道精选题目**：多选题格式，难度递进
- **知识点权重映射**：每题关联1-3个知识点，精确权重标注
- **自动判分支持**：标准答案格式，支持A/B/C/D选择题判分

#### 🔗 语义化嵌入 (`embeddings.csv`)
- **50维向量空间**：每个知识点对应高质量语义向量
- **聚类优化结构**：相关知识点在向量空间中邻近分布
- **质量验证指标**：相关关系平均相似度0.349，前置关系0.312

## 🧠 核心算法

### 1. 智能学生建模

#### 🎯 初始向量计算
```python
# 从初始掌握度生成学生向量
V_student = Σ(mastery_score_i × V_knowledge_point_i) / Σ(mastery_score_i)
# 归一化为单位向量，便于后续计算
```

#### 🔄 动态学习更新
```python
# 迭代学习更新机制
V_new = α × V_old + (1-α) × V_batch
# α=0.7（保留70%历史知识，学习30%新知识）
# 每批次答题后自动更新学生向量
```

#### 📈 正向反馈学习
- **答对题目**：掌握度 += 0.3 × weight（显著提升）
- **答错题目**：掌握度 += 0.1 × weight（仍有学习效果）
- **阈值判定**：掌握度 ≥ 0.5 视为掌握该知识点

### 2. 智能推荐算法

#### 🎯 向量推理核心
```python
# 推荐算法核心公式
V_target = V_mastered + V_prerequisite_relation
# 计算与目标向量最相似的未掌握知识点
similarity = cosine_similarity(V_target, V_candidates)
```

#### ⭐ 多维评分系统
```python
# 综合评分算法
final_score = (
    0.4 × coverage_score +      # 40% - 知识点覆盖程度
    0.3 × relevance_score +     # 30% - 向量相关程度  
    0.2 × difficulty_score +    # 20% - 难度适配度
    0.1 × diversity_score       # 10% - 知识点多样性
)
```

### 3. 🔍 智能诊断功能

#### 薄弱知识点自动识别
```python
# 薄弱知识点诊断算法
weak_points = [kp for kp, score in mastery_scores.items() if score < threshold]
weak_points.sort(key=lambda x: x[1])  # 按掌握度排序
```

#### 📊 个性化学习建议
- **🔴 极低掌握度(0.0-0.1)**：建议重点学习基础概念
- **🟡 较低掌握度(0.1-0.2)**：需要加强练习
- **🟠 一般掌握度(0.2-0.3)**：适量练习巩固
- **💡 策略建议**：根据薄弱知识点数量提供学习策略

#### ⚡ 实时答题判分
```python
# 自动答题判分系统
def check_answer(qid, selected_answer):
    # 支持A/B/C/D选择题自动判分
    # 返回详细的答题分析结果
    return {
        "is_correct": True/False,
        "selected": "C",
        "correct_answer": "正确答案内容",
        "knowledge_points": {"K1": 0.9}
    }
```

## 🎯 API接口说明

### 🚀 主要接口

#### 1. 学习会话管理
```python
# 开始学习会话
api.start_session("student_001", initial_mastery={"K1": 0.3})

# 获取当前状态
status = api.get_session_status()

# 结束会话
api.end_session()
```

#### 2. 智能推荐服务
```python
# 获取个性化推荐题目
questions = api.get_questions(num_questions=3)
# 返回：题目内容、选项、知识点权重、难度等级
```

#### 3. 答题与分析
```python
# 提交答案（自动判分）
answers = [{"qid": "Q1", "selected": "C"}]
result = api.submit_student_answers(answers)

# 独立答案检查
check_result = api.check_answers_only(answers)
```

#### 4. 学习诊断分析
```python
# 获取薄弱知识点分析
weak_analysis = api.get_weak_points(threshold=0.3)
# 返回：薄弱知识点、学习建议、进展统计
```

#### 5. 数据持久化管理
```python
# 导出学生数据（用于B/S架构数据存储）
student_data = api.export_student_data("student_001")

# 导出所有学生数据
all_data = api.export_all_students()

# 从数据恢复学生（服务重启后恢复）
api.import_student_data(student_data)

# 批量恢复所有学生
api.import_all_students(all_data)

# 文件持久化
api.save_student_to_file("student_001", "backup.json")
api.load_student_from_file("backup.json")

# 获取系统中所有学生列表
students_list = api.get_students_list()

### 📊 返回值格式

所有API统一返回JSON格式：
```json
{
    "status": "success/error",
    "message": "操作结果描述", 
    "data": { /* 具体数据内容 */ }
}
```

详细的API文档和返回值格式请参考：
- 📖 [完整API文档](README_API.md)
- ⚡ [API快速参考](API_QUICK_REFERENCE.md)
- � [数据持久化API文档](PERSISTENCE_API_REFERENCE.md)
- 🚀 [推荐算法优化报告](OPTIMIZATION_REPORT.md)
- �📋 [返回值格式示例](api_response_examples.json)

## 🧪 实验效果验证

### 🔬 系统验证结果

#### 📈 嵌入向量质量验证
- **算法类知识点高度相关**：
  - Dijkstra ↔ Floyd: 0.767（最短路径算法族）
  - 最短路径 ↔ Dijkstra: 0.653（概念-实现关系）
- **基础概念递进关系验证**：
  - 集合运算 ↔ 关系映射: 0.655（数学基础递进）
  - 关系映射 ↔ 图基本概念: 0.710（抽象到具体）

#### 🎓 学习效果模拟验证
```
📊 学习轨迹示例：
初始状态: K1(0.2), K2(0.15), K3(0.1), K8(0.05)
5轮学习后: 掌握K3(0.58), K8(0.57)，涉及17个知识点
推荐路径: 基础概念 → 图论基础 → 算法应用（符合认知规律）
```

#### 🎯 推荐质量验证
```
📝 推荐示例分析：
第1轮: Q1(集合), Q7(完全图), Q24(割点) 
       综合评分: 0.821/0.724/0.724
第2轮: Q2(关系), Q11(生成树), Q16(Floyd)
       跨领域平衡推荐
第3轮: Q15(Dijkstra), Q5(树), Q3(入度)
       算法与概念并重策略
```

#### ⚡ 答题判分验证
```
🔍 判分准确性测试：
- 支持A/B/C/D选择题自动判分
- 错误答案显示正确答案
- 实时计算批次准确率
- 答题详情完整记录

📊 薄弱知识点识别准确性：
- 自动识别掌握度<0.3的知识点
- 按掌握度排序，优先显示最薄弱
- 生成个性化学习建议
- 学习策略智能调整
```

## 💡 技术创新亮点

### 1. 🧠 向量化学习建模
- **语义空间表示**：将抽象的知识掌握度映射到连续向量空间
- **迭代学习机制**：模拟真实学习中新旧知识的融合过程
- **正向反馈设计**：即使答错也有学习效果，符合教育心理学原理

### 2. 🎯 智能推荐引擎
- **向量推理算法**：基于向量运算进行知识点推理
- **多维度评分**：综合考虑覆盖度、相关性、难度、多样性
- **自适应调整**：根据学习进展动态调整推荐策略

### 3. 📊 实时学习分析
- **自动答题判分**：即时反馈，提高学习效率
- **薄弱知识点诊断**：精准识别学习短板
- **个性化建议生成**：基于数据分析的学习指导

### 4. 🔗 高质量知识图谱
- **语义化嵌入生成**：基于图拓扑结构的有意义向量
- **关系向量建模**：支持多种知识关系的向量表示
- **质量验证机制**：确保嵌入向量的语义一致性

## 🛠️ 使用指南

### 💻 开发者快速上手

#### 基础使用
```bash
# 克隆项目
git clone [repository-url]
cd transE/recommend

# 激活环境
conda activate dzz

# 运行交互式学习
python start.py interactive
```

#### API集成示例
```python
from start import EducationRecommendationAPI

# 初始化系统
api = EducationRecommendationAPI()

# 创建学生并开始学习
api.start_session("student_001", {
    "K1": 0.3,   # 集合运算：有基础
    "K2": 0.2,   # 关系映射：了解
    "K3": 0.1    # 图基本概念：初学
})

# 获取推荐题目
questions = api.get_questions(3)

# 模拟学生答题
answers = [
    {"qid": "Q1", "selected": "C"},
    {"qid": "Q7", "selected": "C"}, 
    {"qid": "Q24", "selected": "B"}
]

# 提交答案并获取学习分析
result = api.submit_student_answers(answers)
print(f"准确率: {result['accuracy']:.1%}")

# 获取薄弱知识点分析
weak_analysis = api.get_weak_points()
for rec in weak_analysis['recommendations']:
    print(rec)

# 结束会话
api.end_session()
```

### ⚙️ 自定义配置

#### 推荐算法参数调整
```python
# 修改评分权重 (simple_system.py)
final_score = (
    0.5 × coverage_score +      # 增强知识点覆盖
    0.2 × relevance_score +     # 降低相关性权重
    0.2 × difficulty_score +    
    0.1 × diversity_score       
)
```

#### 学习参数配置
```python
# 修改学习率 (config.json)
{
    "learning_rate_alpha": 0.8,        # 更保守的学习率
    "mastery_threshold": 0.6,          # 提高掌握判定标准  
    "difficulty_target": 0.7           # 偏好更难题目
}
```

### 📁 文件结构说明

| 文件类型 | 文件名 | 功能描述 | 状态 |
|---------|--------|----------|------|
| 🚀 **核心系统** | `start.py` | 主启动文件和API接口 | ✅ 完成 |
| 🧠 **推荐引擎** | `simple_system.py` | 核心推荐算法实现 | ✅ 完成 |
| 📖 **API文档** | `README_API.md` | 完整API使用文档 | ✅ 完成 |
| ⚡ **快速参考** | `API_QUICK_REFERENCE.md` | API速查表 | ✅ 完成 |
| 💻 **使用示例** | `api_example.py` | 完整使用示例代码 | ✅ 完成 |
| 📋 **格式参考** | `api_response_examples.py` | 返回值格式生成器 | ✅ 完成 |
| 🔗 **嵌入向量** | `embeddings.csv` | 50维语义嵌入向量 | ✅ 完成 |
| 📊 **知识图谱** | `knowledge_graph.csv` | 知识点关系数据 | ✅ 完成 |
| 📚 **题库** | `question_bank.json` | 25道标准化题目 | ✅ 完成 |
| ⚙️ **配置** | `config.json` | 系统参数配置 | ✅ 完成 |

## 🎯 应用场景

### 🎓 教育机构
- **个性化教学**：为每个学生定制学习路径
- **学习诊断**：识别学生知识薄弱环节
- **教学效果评估**：跟踪学习进展和知识掌握情况

### 💻 在线教育平台
- **智能推荐**：基于学习历史推荐合适题目
- **自适应学习**：动态调整学习内容和难度
- **学习分析**：提供详细的学习报告和建议

### 🔬 教育研究
- **学习模式分析**：研究不同学习策略的效果
- **知识图谱应用**：探索图谱技术在教育中的价值
- **推荐算法评估**：对比不同推荐方法的效果

## 🔮 未来发展规划

### 🎯 短期目标（已完成）
- ✅ **智能答题判分系统**：支持A/B/C/D选择题自动判分
- ✅ **薄弱知识点诊断**：自动识别学习薄弱环节
- ✅ **完整API接口**：为前端集成提供标准化服务
- ✅ **实时学习分析**：提供即时的学习反馈和建议

### 🚀 中期规划
#### 1. 🎚️ 个性化难度适应
- **智能难度调节**：根据学生历史表现动态调整难度偏好
- **能力区间识别**：分析答题正确率，计算个人适应区间
- **实现方案**：`target_difficulty = base_difficulty + personal_offset`

#### 2. 🔄 错题智能重现
- **遗忘曲线建模**：基于遗忘规律设计重现时机
- **掌握度关联**：结合知识点掌握度变化判断复习需求
- **错题池管理**：维护个性化错题库，设计重现概率函数

#### 3. ⚖️ 巩固拓展平衡
- **学习阶段识别**：自动判断学生当前学习阶段
- **策略动态调节**：在巩固已学知识和探索新领域间智能平衡
- **比例优化算法**：基于掌握度分布调整巩固/拓展比例

### 🔬 长期愿景
#### 1. 📊 多模态学习分析
- **学习行为挖掘**：分析答题时间、错误模式等深层特征
- **情感状态识别**：结合学习情感状态优化推荐策略
- **学习风格适配**：识别并适应不同学生的学习偏好

#### 2. 🌐 跨领域知识图谱
- **知识领域扩展**：从图论扩展到更多数学和计算机科学领域
- **跨学科关联**：建立不同学科知识点间的关联关系
- **通用推荐框架**：构建适用于多学科的通用推荐引擎

#### 3. 🤖 AI辅助教学
- **自动题目生成**：基于知识图谱自动生成高质量练习题
- **学习路径规划**：为学生制定长期的个性化学习计划
- **教师辅助工具**：为教师提供学生学习状态分析和教学建议

## 📊 技术栈与依赖

### 🐍 核心技术
- **Python 3.11+**：主要开发语言
- **NumPy**：高性能向量计算
- **Pandas**：数据处理和分析
- **Scikit-learn**：机器学习工具（相似度计算）
- **NetworkX**：图结构分析（嵌入生成）

### 📦 项目依赖
```requirements.txt
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=1.0.0
networkx>=2.6.0
```

### 🔧 开发工具
- **Conda**：环境管理
- **Git**：版本控制
- **JSON**：数据交换格式
- **Markdown**：文档编写

## 👥 项目贡献

### 🎯 核心贡献
- **算法设计**：向量化学习建模和智能推荐算法
- **系统实现**：完整的推荐系统架构和API接口
- **数据构建**：高质量的知识图谱和语义嵌入向量
- **功能完善**：答题判分、学习分析、薄弱知识点诊断
- **文档编写**：详细的API文档和使用指南

### 🌟 创新点总结
1. **向量化知识状态表示**：首创将学生知识掌握状态映射到连续向量空间
2. **基于TransE的教育推荐**：将知识图谱嵌入技术应用于教育推荐场景
3. **多维度智能评分**：综合覆盖度、相关性、难度、多样性的评分机制
4. **实时学习分析系统**：集成答题判分、薄弱诊断、个性化建议的完整分析链

## 📄 许可证与引用

本项目展示了知识图谱嵌入在教育推荐系统中的创新应用，为个性化学习提供了新的技术路径。

### 📖 相关文档
- [完整API文档](README_API.md)
- [API快速参考](API_QUICK_REFERENCE.md)  
- [使用示例代码](api_example.py)
- [返回值格式参考](api_response_examples.json)

---

**🎓 项目意义**：本系统成功将前沿的知识图谱嵌入技术与教育场景深度结合，为智能教育和个性化学习提供了可行的技术方案，具有重要的理论价值和实用价值。
