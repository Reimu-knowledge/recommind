# 教育推荐系统后端API

基于Flask框架的教育推荐系统后端服务，集成了学生数据库存储和智能推荐功能。

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装依赖
pip install -r requirements.txt

# 确保recommend目录下的推荐系统可以正常运行
cd ../recommend
python start.py demo  # 测试推荐系统
```

### 2. 启动服务

```bash
# 简化版启动（推荐）
python app_simple.py

# 或者使用完整版
python run.py
```

服务将在 `http://localhost:5000` 启动

### 3. 健康检查

```bash
curl http://localhost:5000/api/health
```

## 📊 数据库结构

### 学生表 (students)
- `id`: 学生ID (主键)
- `name`: 学生姓名
- `email`: 邮箱
- `grade`: 年级
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `is_active`: 是否激活

### 学习会话表 (learning_sessions)
- `id`: 会话ID (主键)
- `student_id`: 学生ID (外键)
- `session_name`: 会话名称
- `started_at`: 开始时间
- `ended_at`: 结束时间
- `total_questions`: 总题目数
- `correct_answers`: 正确答案数
- `accuracy`: 准确率
- `is_active`: 是否活跃

### 知识点掌握度表 (knowledge_mastery)
- `id`: 记录ID (主键)
- `student_id`: 学生ID (外键)
- `knowledge_point_id`: 知识点ID (K1, K2, etc.)
- `mastery_score`: 掌握度分数 (0.0-1.0)
- `last_updated`: 最后更新时间
- `practice_count`: 练习次数
- `correct_count`: 正确次数

### 答题记录表 (answer_records)
- `id`: 记录ID (主键)
- `student_id`: 学生ID (外键)
- `session_id`: 会话ID (外键)
- `question_id`: 题目ID (Q1, Q2, etc.)
- `selected_answer`: 选择的答案 (A, B, C, D)
- `correct_answer`: 正确答案
- `is_correct`: 是否正确
- `knowledge_points`: 涉及知识点 (JSON)
- `answered_at`: 答题时间

## 🔌 API接口

### 学生管理

#### 创建学生
```http
POST /api/students
Content-Type: application/json

{
  "id": "student_001",
  "name": "张三",
  "email": "zhangsan@example.com",
  "grade": "高一",
  "initial_mastery": {
    "K1": 0.2,
    "K2": 0.1,
    "K3": 0.15
  }
}
```

#### 获取学生信息
```http
GET /api/students/{student_id}
```

#### 获取所有学生
```http
GET /api/students?page=1&per_page=20
```

### 学习会话管理

#### 开始学习会话
```http
POST /api/students/{student_id}/sessions
Content-Type: application/json

{
  "session_name": "数学学习会话"
}
```

#### 结束学习会话
```http
PUT /api/sessions/{session_id}
```

### 推荐系统

#### 获取推荐题目
```http
GET /api/students/{student_id}/recommendations?num_questions=3
```

响应示例：
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

#### 提交答案
```http
POST /api/students/{student_id}/answers
Content-Type: application/json

{
  "session_id": 1,
  "answers": [
    {
      "qid": "Q1",
      "selected": "C"
    },
    {
      "qid": "Q2", 
      "selected": "A"
    }
  ]
}
```

响应示例：
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

### 学习分析

#### 获取知识点掌握情况
```http
GET /api/students/{student_id}/mastery
```

#### 获取薄弱知识点分析
```http
GET /api/students/{student_id}/weak-points?threshold=0.3
```

#### 获取学习历史
```http
GET /api/students/{student_id}/learning-history?page=1&per_page=50
```

## 🎯 使用流程

### 1. 创建学生
```bash
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -d '{
    "id": "student_001",
    "name": "张三",
    "grade": "高一",
    "initial_mastery": {
      "K1": 0.2,
      "K2": 0.1,
      "K3": 0.15
    }
  }'
```

### 2. 开始学习会话
```bash
curl -X POST http://localhost:5000/api/students/student_001/sessions \
  -H "Content-Type: application/json" \
  -d '{"session_name": "数学学习"}'
```

### 3. 获取推荐题目
```bash
curl http://localhost:5000/api/students/student_001/recommendations?num_questions=3
```

### 4. 提交答案
```bash
curl -X POST http://localhost:5000/api/students/student_001/answers \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "answers": [
      {"qid": "Q1", "selected": "C"},
      {"qid": "Q2", "selected": "A"}
    ]
  }'
```

### 5. 查看学习分析
```bash
# 查看知识点掌握情况
curl http://localhost:5000/api/students/student_001/mastery

# 查看薄弱知识点
curl http://localhost:5000/api/students/student_001/weak-points

# 查看学习历史
curl http://localhost:5000/api/students/student_001/learning-history
```

### 6. 结束学习会话
```bash
curl -X PUT http://localhost:5000/api/sessions/1
```

## 🔧 配置说明

### 环境变量
- `FLASK_ENV`: 环境类型 (development/production/testing)
- `HOST`: 服务地址 (默认: 0.0.0.0)
- `PORT`: 服务端口 (默认: 5000)
- `DEBUG`: 调试模式 (默认: True)

### 数据库配置
- 开发环境: SQLite数据库
- 生产环境: 可配置MySQL/PostgreSQL

## 📈 功能特性

### ✅ 已实现功能
- [x] 学生信息管理
- [x] 学习会话管理
- [x] 智能题目推荐
- [x] 自动答题判分
- [x] 知识点掌握度跟踪
- [x] 学习历史记录
- [x] 薄弱知识点分析
- [x] 学习统计分析

### 🚀 推荐算法特性
- **向量化学生建模**: 50维语义向量表示学生知识状态
- **智能推荐**: 基于知识图谱的个性化推荐
- **动态学习**: 实时更新学生模型
- **多维评分**: 综合考虑覆盖度、相关性、难度、多样性

### 📊 数据分析功能
- **学习轨迹追踪**: 记录完整的学习过程
- **知识点掌握分析**: 实时跟踪26个知识点的掌握情况
- **学习效果评估**: 提供准确率、进步趋势等指标
- **个性化建议**: 基于薄弱知识点的学习建议

## 🛠️ 技术栈

- **后端框架**: Flask
- **数据库**: SQLAlchemy + SQLite/MySQL/PostgreSQL
- **推荐引擎**: 基于TransE知识图谱嵌入
- **数据处理**: Pandas, NumPy
- **机器学习**: Scikit-learn

## 📝 注意事项

1. **推荐系统依赖**: 确保 `../recommend` 目录下的推荐系统可以正常运行
2. **数据库初始化**: 首次运行会自动创建数据库表
3. **知识点映射**: 系统使用K1-K26的知识点ID体系
4. **答题格式**: 支持A/B/C/D选择题格式
5. **会话管理**: 建议每次学习都创建新的学习会话

## 🔍 故障排除

### 推荐系统初始化失败
```bash
# 检查recommend目录是否存在
ls ../recommend/

# 测试推荐系统
cd ../recommend
python start.py demo
```

### 数据库连接问题
```bash
# 检查数据库文件权限
ls -la *.db

# 重新初始化数据库
rm *.db
python app_simple.py
```

### API接口测试
```bash
# 使用curl测试接口
curl http://localhost:5000/api/health

# 使用Postman或其他API测试工具
```

## 📞 技术支持

如有问题，请检查：
1. 推荐系统是否正常运行
2. 数据库文件是否可写
3. 端口5000是否被占用
4. 依赖包是否完整安装



