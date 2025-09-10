# 薄弱知识点导航功能更新

## 🎯 问题解决

### 原问题
1. **显示问题**: 薄弱知识点显示的是K13这种编号，而不是知识点名称
2. **导航问题**: 点击薄弱知识点无法导航到相关题目

### 解决方案
1. **知识点名称映射**: 从知识图谱中获取知识点ID到名称的映射
2. **题目导航**: 实现根据知识点ID获取相关题目的功能

## ✨ 新增功能

### 1. 后端API增强

#### 知识点映射数据加载
```python
# 加载知识点映射数据
knowledge_points_mapping = {}
with open('recommend/formatted_nodes.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        knowledge_points_mapping[row['name']] = row['id']
```

#### 题目数据加载
```python
# 加载题目数据
questions_data = {}
with open('recommend/question.json', 'r', encoding='utf-8') as f:
    questions_json = json.load(f)
    for question in questions_json['questions']:
        questions_data[question['qid']] = question
```

### 2. API接口更新

#### 薄弱知识点接口增强
- **URL**: `GET /api/students/{student_id}/weak-points`
- **新响应格式**:
```json
{
  "status": "success",
  "weak_knowledge_points": [
    {
      "id": "K13",
      "name": "顶点的度数",
      "score": 0.25
    }
  ]
}
```

#### 新增知识点题目接口
- **URL**: `GET /api/questions/by-knowledge-point/{knowledge_point_id}`
- **响应格式**:
```json
{
  "status": "success",
  "knowledge_point_id": "K13",
  "knowledge_point_name": "顶点的度数",
  "questions": [
    {
      "qid": "Q1",
      "content": "每个图中度数为奇数的顶点个数为()个",
      "options": ["1", "2", "3", "4"],
      "answer": "2",
      "knowledge_points": {"K35": 0.9, "K13": 0.85},
      "difficulty": 0.5
    }
  ],
  "total_count": 15
}
```

### 3. 前端功能更新

#### API调用更新
```typescript
// 获取薄弱知识点 - 现在返回包含名称的对象
const weakPoints = await studentApi.getWeakKnowledgePoints(studentId);

// 根据知识点获取题目 - 新功能
const questions = await studentApi.getQuestionsByKnowledgePoint(knowledgePointId);
```

#### 薄弱知识点导航
```typescript
const selectWeakPoint = async (point: any) => {
  // 根据知识点ID获取相关题目
  const relatedQuestions = await studentApi.getQuestionsByKnowledgePoint(point.id);
  questions.value = relatedQuestions;
  currentView.value = 'weak';
};
```

## 📊 数据流程

### 1. 知识点名称显示流程
```
后端加载知识点映射 → API返回知识点名称 → 前端显示友好名称
```

### 2. 题目导航流程
```
用户点击薄弱知识点 → 获取知识点ID → 查询相关题目 → 显示专项练习
```

## 🎨 用户界面更新

### 薄弱知识点显示
- **更新前**: K13 (掌握度: 25%)
- **更新后**: 顶点的度数 (掌握度: 25%)

### 题目导航
- **点击薄弱知识点** → 自动跳转到专项练习页面
- **显示相关题目数量** → "已获取'顶点的度数'的15道练习题目！"

## 🧪 测试方法

### 1. 后端测试
```bash
cd backend
python test_knowledge_points.py
```

### 2. 前端测试
1. 启动前端服务
2. 登录学生账号
3. 查看薄弱知识点是否显示名称
4. 点击薄弱知识点测试导航功能

### 3. 手动测试流程
1. **健康检查**: 验证数据加载状态
2. **薄弱知识点**: 验证名称显示
3. **题目导航**: 验证点击跳转功能
4. **题目显示**: 验证相关题目正确加载

## 🔧 技术实现

### 数据映射
- **知识点ID**: K13, K35, K87 等
- **知识点名称**: 顶点的度数, 握手定理, 欧拉图 等
- **映射文件**: `recommend/formatted_nodes.csv`

### 题目匹配
- **匹配逻辑**: 检查题目的 `knowledge_points` 字段
- **权重过滤**: 可以根据知识点权重进行筛选
- **格式转换**: 后端格式转换为前端需要的格式

### 错误处理
- **数据加载失败**: 降级到使用知识点ID
- **题目查询失败**: 显示友好的错误信息
- **网络异常**: 提供重试机制

## 💡 优势

### 1. 用户体验
- **友好显示**: 知识点名称比ID更易理解
- **精准导航**: 直接跳转到相关题目
- **即时反馈**: 显示题目数量信息

### 2. 功能完整性
- **数据完整性**: 知识点ID和名称的完整映射
- **导航准确性**: 基于知识点的精确题目匹配
- **扩展性**: 支持更多知识点和题目类型

### 3. 性能优化
- **数据预加载**: 启动时加载所有映射数据
- **缓存机制**: 避免重复查询
- **批量处理**: 一次性获取所有相关题目

## 🔄 更新日志

### v1.0.0 (当前版本)
- ✅ 实现知识点名称映射
- ✅ 添加知识点题目查询接口
- ✅ 更新薄弱知识点显示格式
- ✅ 实现点击导航功能
- ✅ 完善错误处理机制

### 下一步计划
- 🔄 支持知识点权重筛选
- 🔄 添加题目难度过滤
- 🔄 实现知识点学习进度跟踪
- 🔄 优化题目推荐算法

## 🚨 注意事项

### 1. 数据一致性
- 确保知识点映射文件与题目数据同步
- 定期检查数据更新和映射关系

### 2. 性能考虑
- 大量题目时的加载性能
- 知识点映射的内存占用

### 3. 错误处理
- 知识点ID不存在的情况
- 题目数据格式变化的情况
- 网络请求失败的情况
