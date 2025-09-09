# 知识图谱推荐系统 - 完整API使用指南

## 📖 系统简介

这是一个基于TransE知识图谱嵌入的智能教育推荐系统，集成了个性化推荐、实时学习分析、数据持久化等功能，支持B/S架构部署。系统可以根据学生的学习情况动态推荐合适的题目，并提供完整的学习数据管理方案。

## 🚀 快速开始

### 1. 环境准备
```bash
# 激活conda环境
conda activate dzz

# 确保安装了必要的包
pip install numpy pandas scikit-learn
```

### 2. 运行方式

#### 演示模式（推荐用于快速了解系统）
```bash
python start.py demo
```
- 自动运行3轮学习演示
- 模拟学生答题过程
- 展示系统推荐能力

#### 交互式模式（推荐用于实际学习）
```bash
python start.py interactive
```
- 输入学生ID开始学习
- 系统推荐题目，学生作答
- 实时更新学习状态

#### API模式（用于前端集成）
```python
from start import EducationRecommendationAPI

# 初始化API
api = EducationRecommendationAPI()

# 开始学习会话
api.start_session("student_001")

# 获取推荐题目
questions = api.get_questions(3)

# 提交答案
answers = [
    {
        "qid": "Q1",
        "correct": True,
        "knowledge_points": {"K1": 0.8}
    }
]
api.submit_student_answers(answers)

# 结束会话
api.end_session()
```

## 🎯 核心功能

### 1. 学生建模
- **初始向量计算**: 基于初始知识点掌握度生成50维学生向量
- **动态更新**: 使用公式 `V_new = α * V_old + (1-α) * V_batch` 进行迭代学习
- **正向反馈**: 正确答题时学习强度为1.0，错误时为0.3
- **薄弱知识点分析**: 自动识别学习薄弱环节并提供针对性建议

### 2. 推荐算法
- **冷启动**: 新学生推荐基础题目（K1、K2、K3）
- **向量推理**: 使用 `V_target = V_mastered + V_prerequisite` 计算目标向量
- **多维评分**: 覆盖度(40%) + 相关性(30%) + 难度(20%) + 多样性(10%)

### 3. 答题系统
- **自动判分**: 支持选择题自动判断对错（A/B/C/D选项）
- **实时反馈**: 提供即时的答题结果和正确答案
- **学习追踪**: 记录完整的答题历史和学习轨迹
- **准确率统计**: 实时计算答题准确率和学习效果

### 4. 知识图谱
- **26个知识点**: K1-K26涵盖图论核心概念
- **语义嵌入**: 50维有意义向量，基于图拓扑结构生成
- **关系建模**: 前置关系和相关关系向量

## 📁 文件结构

```
recommend/
├── start.py                      # 主启动文件，提供命令行和API接口
├── simple_system.py              # 核心推荐系统逻辑
├── api_example.py               # API使用示例和功能演示
├── api_response_examples.py     # API返回值格式示例生成器
├── api_response_examples.json   # API返回值格式参考文件
├── embeddings.csv               # 知识点嵌入向量（50维）
├── knowledge_graph.csv          # 知识图谱关系数据
├── question_bank.json           # 题库（25道题目）
├── config.json                  # 系统配置文件
└── README_API.md               # 本文档
```

## 🔧 API接口说明

### EducationRecommendationAPI 类

#### 主要方法及返回值格式：

### 1. start_session(student_id, initial_mastery=None)
**功能**: 开始学习会话  
**参数**: 
- `student_id` (str): 学生ID
- `initial_mastery` (dict, 可选): 初始知识点掌握度，如 `{"K1": 0.3, "K2": 0.1}`

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001", 
    "initial_mastery": {
        "K1": 0.1,
        "K2": 0.1,
        "K3": 0.05
    },
    "message": "学生 student_001 创建成功"
}
```

### 2. get_questions(num_questions=3)
**功能**: 获取推荐题目  
**参数**: 
- `num_questions` (int): 推荐题目数量，默认3道

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001",
    "recommendations": [
        {
            "qid": "Q1",
            "content": "集合A={1,2,3}，集合B={2,3,4}，求A∪B",
            "options": [
                "{1,2,3}",
                "{2,3}", 
                "{1,2,3,4}",
                "{4}"
            ],
            "knowledge_points": {
                "K1": 0.9
            },
            "difficulty": 0.5
        }
    ],
    "batch_number": 1
}
```

### 3. submit_student_answers(answers)
**功能**: 提交学生答案（自动判断对错）  
**参数**: 
- `answers` (list): 答案列表，格式 `[{"qid": "Q1", "selected": "A"}]`

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001",
    "batch_completed": 1,
    "current_mastery": {
        "K1": 0.370,
        "K2": 0.100,
        "K3": 0.530
    },
    "mastered_knowledge_points": ["K3"],
    "answer_details": [
        {
            "qid": "Q1",
            "correct": true,
            "knowledge_points": {"K1": 0.9},
            "selected": "C",
            "correct_answer": "{1,2,3,4}"
        }
    ]
}
```

### 4. check_answers_only(answers)
**功能**: 仅检查答案正确性，不更新学生模型  
**参数**: 
- `answers` (list): 答案列表，格式 `[{"qid": "Q1", "selected": "A"}]`

**返回值格式**:
```json
{
    "status": "success",
    "total_questions": 4,
    "correct_count": 3,
    "accuracy": 0.75,
    "details": [
        {
            "status": "success",
            "qid": "Q1",
            "selected": "C",
            "selected_option": "{1,2,3,4}",
            "correct_answer": "{1,2,3,4}",
            "is_correct": true,
            "knowledge_points": {"K1": 0.9}
        },
        {
            "status": "success", 
            "qid": "Q2",
            "selected": "B",
            "selected_option": "R={(2,2)}",
            "correct_answer": "R={(1,1),(2,2)}",
            "is_correct": false,
            "knowledge_points": {"K2": 0.8}
        }
    ]
}
```

### 5. get_weak_points(threshold=0.3)
**功能**: 获取学生薄弱知识点分析  
**参数**: 
- `threshold` (float): 薄弱知识点判定阈值，默认0.3

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001",
    "weak_knowledge_points": [
        ["K2", 0.100],
        ["K8", 0.180],
        ["K6", 0.210]
    ],
    "progress_summary": {
        "total_knowledge_points": 4,
        "mastered": 1,
        "moderate": 1,
        "weak": 2,
        "mastered_list": ["K1"],
        "weak_list": ["K2", "K8"],
        "average_mastery": 0.323
    },
    "recommendations": [
        "🟡 K2 掌握度较低(0.10)，需要加强练习",
        "🟡 K8 掌握度较低(0.18)，需要加强练习",
        "💡 建议：集中精力攻克这些薄弱知识点，很快就能看到明显进步"
    ]
}
```

### 6. get_session_status()
**功能**: 获取当前学习状态  

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001",
    "batch_count": 2,
    "total_questions": 6,
    "mastery_scores": {
        "K1": 0.370,
        "K2": 0.100,
        "K3": 0.530,
        "K8": 0.180
    },
    "mastered_knowledge_points": ["K3"],
    "vector_norm": 1.0
}
```

### 7. end_session()
**功能**: 结束学习会话  

**返回值格式**:
```json
{
    "status": "success",
    "message": "会话 student_001 已成功结束",
    "final_status": {
        "status": "success",
        "student_id": "student_001",
        "batch_count": 3,
        "total_questions": 8,
        "mastery_scores": {
            "K1": 0.450,
            "K2": 0.200,
            "K3": 0.650
        },
        "mastered_knowledge_points": ["K3"],
        "vector_norm": 1.0
    }
}
```

## 📊 系统特点

### 技术优势
1. **向量化学习**: 使用50维向量表示学生知识状态
2. **语义推理**: 基于知识图谱进行智能推荐
3. **动态适应**: 实时调整推荐策略
4. **多维评估**: 综合考虑多个评分维度

### 教育价值
1. **个性化**: 根据每个学生的学习情况定制推荐
2. **渐进式**: 由易到难，循序渐进
3. **反馈驱动**: 基于学习效果动态调整
4. **知识建构**: 遵循知识前置关系

## 📋 错误响应格式

所有API方法在出现错误时都会返回统一的错误格式：

```json
{
    "status": "error",
    "message": "具体错误信息描述"
}
```

**常见错误情况**:
- 学生不存在: `"学生 {student_id} 不存在"`
- 没有活跃会话: `"没有活跃的学习会话，请先开始会话"`
- 答案格式错误: `"答案格式错误，需要包含字段: ['qid', 'selected']"`
- 题目不存在: `"题目 {qid} 不存在"`

## 📊 数据字段说明

### 知识点掌握度 (mastery_scores)
- **数据类型**: `Dict[str, float]`
- **取值范围**: 0.0 - 1.0
- **含义**: 
  - 0.0-0.3: 薄弱
  - 0.3-0.5: 中等
  - 0.5-1.0: 掌握

### 题目难度 (difficulty)
- **数据类型**: `float`
- **取值范围**: 0.0 - 1.0
- **含义**: 0.0为最简单，1.0为最困难

### 知识点权重 (knowledge_points)
- **数据类型**: `Dict[str, float]`
- **取值范围**: 0.0 - 1.0
- **含义**: 该题目对各知识点的覆盖程度

### 向量范数 (vector_norm)
- **数据类型**: `float`
- **含义**: 学生向量的模长，通常为1.0（单位向量）

### 准确率 (accuracy)
- **数据类型**: `float`
- **取值范围**: 0.0 - 1.0
- **含义**: 答题正确率，1.0表示100%正确

## 📝 API使用示例

### 完整使用流程示例
```python
from start import EducationRecommendationAPI

# 1. 初始化API
api = EducationRecommendationAPI()

# 2. 开始学习会话
session_result = api.start_session("student_001", {
    "K1": 0.2,  # 集合运算有基础
    "K2": 0.1,  # 关系映射较薄弱
    "K3": 0.15  # 图基本概念略有了解
})

if session_result["status"] == "success":
    print(f"学生创建成功，初始掌握度: {session_result['initial_mastery']}")
    
    # 3. 获取推荐题目
    questions_result = api.get_questions(3)
    if questions_result["status"] == "success":
        print(f"推荐 {len(questions_result['recommendations'])} 道题目")
        
        # 4. 模拟答题
        answers = []
        for q in questions_result['recommendations']:
            # 这里应该是用户的实际选择
            user_choice = "C"  # 示例选择
            answers.append({"qid": q["qid"], "selected": user_choice})
        
        # 5. 提交答案
        submit_result = api.submit_student_answers(answers)
        if submit_result["status"] == "success":
            print(f"答题完成，准确率: {len([d for d in submit_result['answer_details'] if d['correct']]) / len(submit_result['answer_details']) * 100:.1f}%")
            print(f"当前掌握知识点: {submit_result['mastered_knowledge_points']}")
            
            # 6. 获取薄弱知识点分析
            weak_analysis = api.get_weak_points(0.3)
            if weak_analysis["status"] == "success":
                weak_count = len(weak_analysis["weak_knowledge_points"])
                print(f"薄弱知识点数量: {weak_count}")
                for recommendation in weak_analysis["recommendations"]:
                    print(f"建议: {recommendation}")
        
        # 7. 结束会话
        end_result = api.end_session()
        print(f"会话结束: {end_result['message']}")
```

### 独立答案检查示例
```python
# 仅检查答案，不影响学生模型
check_answers = [
    {"qid": "Q1", "selected": "C"},
    {"qid": "Q2", "selected": "A"},
    {"qid": "Q3", "selected": "B"}
]

check_result = api.check_answers_only(check_answers)
if check_result["status"] == "success":
    print(f"检查结果: {check_result['correct_count']}/{check_result['total_questions']} 正确")
    print(f"准确率: {check_result['accuracy']:.1%}")
    
    for detail in check_result["details"]:
        if detail["is_correct"]:
            print(f"✅ {detail['qid']}: {detail['selected']}")
        else:
            print(f"❌ {detail['qid']}: {detail['selected']} (正确答案: {detail['correct_answer']})")
```

## 🎓 使用建议

### 对于教师
- 使用演示模式了解系统能力
- 观察学生学习轨迹和知识点掌握情况
- 根据推荐结果调整教学策略

### 对于学生
- 使用交互式模式进行个性化学习
- 关注知识点掌握度的变化
- 按照系统推荐循序渐进学习

### 对于开发者
- 使用API模式集成到现有系统
- 可扩展更多知识点和题目
- 可调整推荐算法参数

## 🔍 技术细节

### 学习向量更新
```python
# α=0.7 表示保留70%的历史知识，学习30%的新知识
V_new = 0.7 * V_old + 0.3 * V_batch
```

### 推荐评分计算
```python
final_score = (
    0.4 * coverage_score +      # 知识点覆盖度
    0.3 * relevance_score +     # 向量相似度
    0.2 * difficulty_score +    # 难度匹配度
    0.1 * diversity_score       # 知识点多样性
)
```

### 掌握度更新
```python
if correct:
    mastery += 0.3 * weight  # 正确答题增加掌握度
else:
    mastery += 0.1 * weight  # 错误答题也有少量提升
```

## � 数据持久化API（B/S架构支持）

### 8. export_student_data(student_id=None)
**功能**: 导出学生数据用于持久化存储  
**参数**: 
- `student_id` (str, 可选): 学生ID，不提供则使用当前会话学生

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001",
    "data": {
        "student_id": "student_001",
        "embedding_dim": 50,
        "mastery_scores": {"K1": 0.3, "K2": 0.2},
        "question_history": [...],
        "batch_count": 3,
        "vector": [...],
        "export_timestamp": 1725544234.567,
        "version": "1.1"
    },
    "export_timestamp": 1725544234.567,
    "message": "学生 student_001 数据导出成功"
}
```

### 9. import_student_data(student_data)
**功能**: 从持久化数据恢复学生对象  
**参数**: 
- `student_data` (dict): 通过export_student_data导出的数据

**返回值格式**:
```json
{
    "status": "success",
    "student_id": "student_001",
    "batch_count": 3,
    "total_questions": 9,
    "message": "学生 student_001 数据恢复成功"
}
```

### 10. export_all_students()
**功能**: 导出所有学生数据

**返回值格式**:
```json
{
    "status": "success",
    "data": {
        "student_001": {...},
        "student_002": {...}
    },
    "student_count": 2,
    "export_timestamp": 1725544234.567,
    "message": "成功导出 2 个学生的数据"
}
```

### 11. import_all_students(students_data)
**功能**: 批量恢复学生数据  
**参数**: 
- `students_data` (dict): 通过export_all_students导出的数据

**返回值格式**:
```json
{
    "status": "success",
    "success_count": 2,
    "error_count": 0,
    "errors": [],
    "message": "成功恢复 2 个学生，失败 0 个"
}
```

### 12. get_students_list()
**功能**: 获取当前系统中所有学生的基本信息

**返回值格式**:
```json
{
    "status": "success",
    "students": [
        {
            "student_id": "student_001",
            "batch_count": 3,
            "total_questions": 9,
            "mastered_knowledge_points": 2,
            "average_mastery": 0.234,
            "last_activity": 1725544234.567
        }
    ],
    "total_count": 1,
    "message": "当前系统中有 1 个学生"
}
```

### 13. 文件持久化API

#### save_student_to_file(student_id=None, file_path=None)
保存学生数据到JSON文件

#### load_student_from_file(file_path)
从JSON文件加载学生数据

#### save_all_students_to_file(file_path=None)
保存所有学生数据到JSON文件

#### load_all_students_from_file(file_path)
从JSON文件加载所有学生数据

### 14. clear_all_students()
**功能**: 清空所有学生数据（谨慎使用）

**返回值格式**:
```json
{
    "status": "success",
    "cleared_count": 3,
    "message": "已清空 3 个学生的数据"
}
```

## 🏗️ B/S架构集成示例

### 数据库集成
```python
class StudentDataManager:
    def __init__(self):
        self.api = EducationRecommendationAPI()
    
    def backup_to_database(self):
        """定时备份到数据库"""
        export_result = self.api.export_all_students()
        if export_result["status"] == "success":
            # 保存到数据库
            save_to_database(export_result["data"])
    
    def restore_from_database(self):
        """服务启动时恢复数据"""
        backup_data = get_latest_backup_from_database()
        if backup_data:
            self.api.import_all_students(backup_data)
```

### 实时同步
```python
def on_student_answer_submitted(student_id):
    """学生答题后实时备份"""
    export_result = api.export_student_data(student_id)
    if export_result["status"] == "success":
        save_student_to_database(student_id, export_result["data"])
```

## �📈 系统效果

- **学习轨迹追踪**: 记录每个批次的学习向量变化
- **知识点掌握**: 实时更新26个知识点的掌握程度
- **推荐准确性**: 基于向量相似度和知识图谱关系
- **学习效率**: 避免重复练习，聚焦薄弱环节
- **数据持久化**: 完整的B/S架构数据存储和恢复方案
- **个性化优化**: 支持遗忘曲线建模和个性化权重调整

## 📋 相关文档

- [数据持久化API详细文档](PERSISTENCE_API_REFERENCE.md)
- [推荐算法优化报告](OPTIMIZATION_REPORT.md)
- [API快速参考](API_QUICK_REFERENCE.md)
- [使用示例代码](api_example.py)
- [数据持久化演示](persistence_demo.py)

---

**开发者**: 基于TransE知识图谱嵌入技术  
**版本**: 2.0  
**更新时间**: 2025年9月
