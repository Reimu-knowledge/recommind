# 知识图谱推荐系统 API 快速参考

## 🚀 快速开始
```python
from start import EducationRecommendationAPI
api = EducationRecommendationAPI()
```

## 📋 API方法速查表

| 方法 | 功能 | 参数 | 主要返回字段 |
|------|------|------|-------------|
| `start_session(id, mastery?)` | 开始会话 | student_id, initial_mastery? | status, student_id, initial_mastery |
| `get_questions(num?)` | 获取推荐题目 | num_questions=3 | status, recommendations[], batch_number |
| `submit_student_answers(answers)` | 提交答案 | [{"qid", "selected"}] | status, current_mastery, answer_details[] |
| `check_answers_only(answers)` | 仅检查答案 | [{"qid", "selected"}] | status, accuracy, details[] |
| `get_weak_points(threshold?)` | 薄弱知识点 | threshold=0.3 | status, weak_knowledge_points[], recommendations[] |
| `get_session_status()` | 会话状态 | 无 | status, batch_count, mastery_scores |
| `end_session()` | 结束会话 | 无 | status, message, final_status |
| **💾 数据持久化API** |
| `export_student_data(id?)` | 导出学生数据 | student_id? | status, data, export_timestamp |
| `import_student_data(data)` | 导入学生数据 | student_data | status, student_id, batch_count |
| `export_all_students()` | 导出所有学生 | 无 | status, data{}, student_count |
| `import_all_students(data)` | 导入所有学生 | students_data | status, success_count, error_count |
| `save_student_to_file(id?, path?)` | 保存到文件 | student_id?, file_path? | status, file_path |
| `load_student_from_file(path)` | 从文件加载 | file_path | status, student_id |
| `get_students_list()` | 获取学生列表 | 无 | status, students[], total_count |
| `clear_all_students()` | 清空所有学生 | 无 | status, cleared_count |

## 📊 核心数据结构

### 推荐题目格式
```json
{
  "qid": "Q1",
  "content": "题目内容...",
  "options": ["选项A", "选项B", "选项C", "选项D"],
  "knowledge_points": {"K1": 0.9},
  "difficulty": 0.5
}
```

### 答案提交格式
```json
[
  {"qid": "Q1", "selected": "C"},
  {"qid": "Q2", "selected": "A"}
]
```

### 知识点掌握度
```json
{
  "K1": 0.37,  // 0.0-0.3: 薄弱
  "K2": 0.10,  // 0.3-0.5: 中等  
  "K3": 0.53   // 0.5-1.0: 掌握
}
```

## ⚡ 常用流程

### 1. 基础学习流程
```python
# 开始会话
api.start_session("student_001")

# 获取题目 → 用户答题 → 提交答案
questions = api.get_questions(3)
answers = [{"qid": "Q1", "selected": "C"}]  # 用户选择
result = api.submit_student_answers(answers)

# 结束会话
api.end_session()
```

### 2. 答案检查流程
```python
# 独立检查答案（不影响学生模型）
check_answers = [{"qid": "Q1", "selected": "C"}]
result = api.check_answers_only(check_answers)
print(f"准确率: {result['accuracy']:.1%}")
```

### 3. 学习分析流程
```python
# 获取薄弱知识点分析
weak_analysis = api.get_weak_points(0.3)
weak_points = weak_analysis['weak_knowledge_points']
recommendations = weak_analysis['recommendations']
```

### 4. 数据持久化流程
```python
# B/S架构数据备份
all_data = api.export_all_students()
# 保存到数据库...

# 服务重启后恢复
api.import_all_students(all_data)

# 文件备份单个学生
api.save_student_to_file("student_001", "backup.json")
api.load_student_from_file("backup.json")
```

## 🔍 错误处理

所有API统一返回格式:
```json
// 成功
{"status": "success", ...}

// 失败  
{"status": "error", "message": "错误描述"}
```

## 📁 参考文件

- `README_API.md` - 完整API文档
- `PERSISTENCE_API_REFERENCE.md` - 数据持久化API详细文档
- `api_example.py` - 使用示例代码
- `persistence_demo.py` - 数据持久化演示
- `api_response_examples.json` - 返回值格式参考
