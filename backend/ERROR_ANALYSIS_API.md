# 错因分析API接口文档

## 📋 接口概述

错因分析模块提供了基于题目ID和选项的智能错因分析功能，帮助学生理解错误原因并提供个性化学习建议。

## 🔌 API接口

### 1. 获取单个选项错因分析

**接口地址**: `GET /api/error-analysis/{question_id}/{option_letter}`

**参数说明**:
- `question_id`: 题目ID (如: Q1, Q2, Q3...)
- `option_letter`: 选项字母 (A, B, C, D)

**请求示例**:
```bash
curl http://localhost:5000/api/error-analysis/Q1/A
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "question_id": "Q1",
    "selected_option": "A",
    "knowledge_points_to_review": [
      {
        "knowledge_point": "握手定理",
        "similarity": 1.0,
        "priority": "high"
      },
      {
        "knowledge_point": "图的表示方法",
        "similarity": 0.5388,
        "priority": "medium"
      }
    ]
  }
}
```

### 2. 获取题目完整错因分析

**接口地址**: `GET /api/error-analysis/{question_id}`

**参数说明**:
- `question_id`: 题目ID (如: Q1, Q2, Q3...)

**请求示例**:
```bash
curl http://localhost:5000/api/error-analysis/Q1
```

**响应示例**:
```json
{
  "status": "success",
  "data": {
    "question_id": "Q1",
    "question_text": "每个图中度数为奇数的顶点个数为()个",
    "options_analysis": {
      "A": {
        "option_text": "1",
        "knowledge_points_to_review": [
          {
            "knowledge_point": "握手定理",
            "similarity": 1.0
          },
          {
            "knowledge_point": "图的表示方法",
            "similarity": 0.5388
          }
        ],
        "review_count": 2
      },
      "B": {
        "option_text": "2",
        "knowledge_points_to_review": [
          {
            "knowledge_point": "握手定理",
            "similarity": 1.0
          }
        ],
        "review_count": 1
      },
      "C": {
        "option_text": "3",
        "knowledge_points_to_review": [],
        "review_count": 0
      },
      "D": {
        "option_text": "4",
        "knowledge_points_to_review": [
          {
            "knowledge_point": "握手定理",
            "similarity": 1.0
          }
        ],
        "review_count": 1
      }
    }
  }
}
```

## 📊 数据结构说明

### 需要巩固的知识点
```json
{
  "knowledge_point": "握手定理",   // 需要巩固的知识点名称
  "similarity": 1.0,              // 相似度分数 (0-1)
  "priority": "high"              // 优先级: high(≥0.8) 或 medium(0.5-0.8)
}
```

### 优先级说明
- **high** (≥0.8): 高优先级，需要重点巩固
- **medium** (0.5-0.8): 中等优先级，需要加强理解
- **低相关** (<0.5): 不显示，无需特别巩固

## 🎯 使用场景

### 1. 学生答题后错因分析
```javascript
// 前端调用示例
async function analyzeError(questionId, selectedOption) {
  const response = await fetch(`/api/error-analysis/${questionId}/${selectedOption}`);
  const data = await response.json();
  
  if (data.status === 'success') {
    const analysis = data.data;
    
    // 显示需要巩固的知识点
    console.log('需要巩固的知识点:', analysis.knowledge_points_to_review);
    
    // 按优先级显示
    analysis.knowledge_points_to_review.forEach(kp => {
      const priority = kp.priority === 'high' ? '🔴 重点' : '🟡 加强';
      console.log(`${priority}: ${kp.knowledge_point}`);
    });
  }
}
```

### 2. 题目预览和教学准备
```javascript
// 获取题目所有选项的错因分析
async function getQuestionAnalysis(questionId) {
  const response = await fetch(`/api/error-analysis/${questionId}`);
  const data = await response.json();
  
  if (data.status === 'success') {
    const analysis = data.data;
    
    // 分析每个选项需要巩固的知识点
    Object.entries(analysis.options_analysis).forEach(([option, info]) => {
      console.log(`选项${option}: ${info.review_count}个需要巩固的知识点`);
      
      // 显示需要巩固的知识点
      info.knowledge_points_to_review.forEach(kp => {
        console.log(`  - ${kp.knowledge_point} (相似度: ${kp.similarity})`);
      });
    });
  }
}
```

## 🔧 错误处理

### 常见错误码
- `400`: 缺少必要参数
- `404`: 题目或选项不存在
- `500`: 服务器内部错误

### 错误响应示例
```json
{
  "status": "error",
  "message": "题目 Q999 不存在"
}
```

## 📈 性能优化

### 1. 数据预加载
错因分析数据在服务启动时预加载到内存中，查询响应速度快。

### 2. 缓存机制
- 数据在内存中缓存，避免重复文件读取
- 支持热重载，数据更新后自动刷新

### 3. 批量查询
支持一次查询获取题目的所有选项分析，减少网络请求次数。

## 🧪 测试方法

### 运行测试脚本
```bash
cd backend
python test_error_analysis.py
```

### 手动测试
```bash
# 测试单个选项
curl http://localhost:5000/api/error-analysis/Q1/A

# 测试完整题目
curl http://localhost:5000/api/error-analysis/Q1

# 测试错误情况
curl http://localhost:5000/api/error-analysis/Q999/A  # 不存在的题目
curl http://localhost:5000/api/error-analysis/Q1/E    # 不存在的选项
```

## 💡 最佳实践

### 1. 前端集成
- 在学生答题后立即调用错因分析接口
- 根据相似度分级显示不同颜色的知识点标签
- 提供个性化的学习建议

### 2. 教学应用
- 教师可以使用完整题目分析了解各选项的知识点分布
- 根据错因分析数据调整教学重点
- 为学生提供针对性的学习资源推荐

### 3. 数据分析
- 收集学生的错因分析数据
- 分析常见错误模式和薄弱知识点
- 优化题库和推荐算法

## 🔍 技术细节

### 数据来源
- 错因分析数据来自 `data/aligned_options_by_question.json`
- 包含每道题每个选项的知识点对齐信息
- 支持相似度评分和知识点映射

### 算法特点
- 基于知识图谱的语义对齐
- 多维度相似度计算
- 智能学习建议生成

### 扩展性
- 支持新增题目和选项
- 可扩展相似度计算算法
- 支持自定义学习建议模板
