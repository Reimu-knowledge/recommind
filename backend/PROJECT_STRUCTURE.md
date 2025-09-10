# 教育推荐系统后端项目结构

## 📁 项目目录结构

```
backend/
├── app.py                 # 完整版主应用文件
├── app_simple.py          # 简化版主应用文件（推荐使用）
├── run.py                 # 应用启动文件
├── models.py              # 数据库模型定义
├── services.py            # 业务逻辑服务层
├── api_routes.py          # API路由定义
├── config.py              # 配置文件
├── test_api.py            # API测试脚本
├── requirements.txt       # Python依赖包
├── README.md              # 使用说明文档
└── PROJECT_STRUCTURE.md   # 项目结构说明（本文件）
```

## 🎯 核心文件说明

### 1. 应用启动文件

#### `app_simple.py` (推荐使用)
- **功能**: 简化版主应用，包含所有核心功能
- **特点**: 单文件实现，易于理解和部署
- **适用**: 快速开发、测试、演示

#### `app.py` (完整版)
- **功能**: 完整版主应用，模块化设计
- **特点**: 代码结构清晰，易于扩展
- **适用**: 生产环境、大型项目

#### `run.py`
- **功能**: 应用工厂模式启动文件
- **特点**: 支持多环境配置
- **适用**: 生产环境部署

### 2. 数据层文件

#### `models.py`
- **功能**: 数据库模型定义
- **包含**: Student, LearningSession, KnowledgeMastery, AnswerRecord等模型
- **特点**: 完整的ORM映射和关系定义

#### `services.py`
- **功能**: 业务逻辑服务层
- **包含**: StudentService, LearningSessionService等业务服务
- **特点**: 封装数据库操作，提供业务接口

### 3. API层文件

#### `api_routes.py`
- **功能**: API路由定义
- **包含**: 所有RESTful API接口
- **特点**: 模块化路由，易于维护

### 4. 配置文件

#### `config.py`
- **功能**: 应用配置管理
- **包含**: 开发、生产、测试环境配置
- **特点**: 环境变量支持，配置分离

## 🚀 快速开始指南

### 1. 环境准备
```bash
# 安装依赖
pip install -r requirements.txt

# 检查推荐系统
cd ../recommend
python start.py demo
```

### 2. 启动服务
```bash
# 方式1: 使用简化版（推荐）
python app_simple.py

# 方式2: 使用完整版
python app.py

# 方式3: 使用工厂模式
python run.py
```

### 3. 测试API
```bash
# 运行API测试
python test_api.py

# 手动测试健康检查
curl http://localhost:5000/api/health
```

## 📊 数据库设计

### 核心表结构

#### 学生表 (students)
```sql
CREATE TABLE students (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE,
    grade VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 学习会话表 (learning_sessions)
```sql
CREATE TABLE learning_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) REFERENCES students(id),
    session_name VARCHAR(100),
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    total_questions INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    accuracy FLOAT DEFAULT 0.0,
    is_active BOOLEAN DEFAULT TRUE
);
```

#### 知识点掌握度表 (knowledge_mastery)
```sql
CREATE TABLE knowledge_mastery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) REFERENCES students(id),
    knowledge_point_id VARCHAR(20) NOT NULL,
    mastery_score FLOAT DEFAULT 0.0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
    practice_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    UNIQUE(student_id, knowledge_point_id)
);
```

#### 答题记录表 (answer_records)
```sql
CREATE TABLE answer_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id VARCHAR(50) REFERENCES students(id),
    session_id INTEGER REFERENCES learning_sessions(id),
    question_id VARCHAR(20) NOT NULL,
    selected_answer VARCHAR(10) NOT NULL,
    correct_answer VARCHAR(10) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    knowledge_points TEXT NOT NULL,
    answered_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🔌 API接口设计

### RESTful API规范

#### 基础URL
```
http://localhost:5000/api
```

#### 接口分类

##### 学生管理
- `POST /students` - 创建学生
- `GET /students/{id}` - 获取学生信息
- `GET /students` - 获取学生列表

##### 学习会话
- `POST /students/{id}/sessions` - 开始学习会话
- `PUT /sessions/{id}` - 结束学习会话

##### 推荐系统
- `GET /students/{id}/recommendations` - 获取推荐题目
- `POST /students/{id}/answers` - 提交答案

##### 学习分析
- `GET /students/{id}/mastery` - 获取知识点掌握情况
- `GET /students/{id}/weak-points` - 获取薄弱知识点分析
- `GET /students/{id}/learning-history` - 获取学习历史

### 响应格式

#### 成功响应
```json
{
  "status": "success",
  "message": "操作成功",
  "data": { ... }
}
```

#### 错误响应
```json
{
  "status": "error",
  "message": "错误信息"
}
```

## 🎯 核心功能流程

### 1. 学生注册流程
```
创建学生 → 初始化掌握度 → 启动推荐系统会话
```

### 2. 学习推荐流程
```
获取推荐题目 → 学生答题 → 提交答案 → 更新掌握度 → 生成新推荐
```

### 3. 学习分析流程
```
收集学习数据 → 分析掌握情况 → 识别薄弱点 → 生成学习建议
```

## 🛠️ 技术架构

### 分层架构
```
API层 (Flask Routes)
    ↓
服务层 (Business Logic)
    ↓
数据层 (SQLAlchemy Models)
    ↓
数据库 (SQLite/MySQL/PostgreSQL)
```

### 推荐系统集成
```
后端API ←→ 推荐引擎 (start.py)
    ↓
知识图谱嵌入 (TransE)
    ↓
智能推荐算法
```

## 📈 扩展指南

### 1. 添加新的API接口
1. 在 `api_routes.py` 中添加路由
2. 在 `services.py` 中添加业务逻辑
3. 在 `models.py` 中添加数据模型（如需要）

### 2. 添加新的数据表
1. 在 `models.py` 中定义新模型
2. 运行数据库迁移
3. 更新相关服务层代码

### 3. 集成新的推荐算法
1. 修改 `recommend/` 目录下的推荐系统
2. 更新API接口调用方式
3. 调整数据格式和参数

## 🔧 部署指南

### 开发环境
```bash
python app_simple.py
```

### 生产环境
```bash
# 使用Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app_simple:app

# 使用Docker
docker build -t education-backend .
docker run -p 5000:5000 education-backend
```

### 环境变量配置
```bash
export FLASK_ENV=production
export DATABASE_URL=mysql://user:pass@localhost/db
export SECRET_KEY=your-secret-key
```

## 📝 注意事项

1. **推荐系统依赖**: 确保 `../recommend` 目录可访问
2. **数据库初始化**: 首次运行会自动创建表结构
3. **知识点映射**: 使用K1-K26的知识点ID体系
4. **会话管理**: 建议每次学习创建新会话
5. **错误处理**: 所有API都有统一的错误处理机制

## 🆘 故障排除

### 常见问题

#### 1. 推荐系统初始化失败
```bash
# 检查推荐系统
cd ../recommend
python start.py demo
```

#### 2. 数据库连接问题
```bash
# 检查数据库文件
ls -la *.db

# 重新初始化
rm *.db
python app_simple.py
```

#### 3. 端口占用问题
```bash
# 检查端口占用
netstat -an | grep 5000

# 修改端口
export PORT=5001
python app_simple.py
```

## 📞 技术支持

如有问题，请按以下顺序检查：
1. 推荐系统是否正常运行
2. 数据库文件是否可写
3. 依赖包是否完整安装
4. 端口是否被占用
5. 配置文件是否正确
