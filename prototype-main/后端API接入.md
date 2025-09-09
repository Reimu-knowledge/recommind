# 后端API接入

## API配置

### 后端地址配置
在 `src/api/student.ts` 中修改API地址：
```typescript
const API_BASE_URL = 'http://localhost:8080'  // 修改为实际后端地址
```

### 前端调用代码位置
- 文件位置：`src/api/student.ts`
- 真实API代码已注释，需要时取消注释即可
- 当前使用的是模拟数据

## API接口

### 1. 获取推荐题目

**URL:** `POST /api/student/recommend-questions`

**请求头:**
```
Content-Type: application/json
```

**请求体:**
```json
{
  "studentId": "1120220001",
  "knowledgePoints": ["basic", "euler"]  // 可选，空数组表示系统自动推荐
}
```

**响应格式:**
```json
{
  "code": 200,
  "message": "推荐题目获取成功",
  "data": {
    "questions": [
      {
        "questionId": "q001",
        "description": "题目描述",
        "knowledgePoint": "basic",
        "knowledgePointName": "图的基本概念",
        "options": [
          {"id": "A", "text": "选项A"},
          {"id": "B", "text": "选项B"},
          {"id": "C", "text": "选项C"},
          {"id": "D", "text": "选项D"}
        ]
      }
    ]
  }
}
```

### 2. 提交答案

**URL:** `POST /api/student/submit-answer`

**请求头:**
```
Content-Type: application/json
```

**请求体:**
```json
{
  "questionId": "q001",
  "studentId": "1120220001", 
  "selectedOption": "B"
}
```

**响应格式:**
```json
{
  "code": 200,
  "message": "答案提交成功",
  "data": {
    "isCorrect": true,
    "correctAnswer": "B"
  }
}
```

### 3. 获取题目解析

**URL:** `POST /api/student/get-explanation`

**请求头:**
```
Content-Type: application/json
```

**请求体:**
```json
{
  "questionId": "q001",
  "studentId": "1120220001",
  "selectedOption": "B"
}
```

**响应格式:**
```json
{
  "code": 200,
  "message": "解析获取成功", 
  "data": {
    "explanation": "这道题考查的是图的基本概念..."
  }
}
```

### 4. 获取薄弱知识点

**URL:** `GET /api/student/weak-knowledge-points?studentId=1120220001`

**请求头:**
```
Content-Type: application/json
```

**响应格式:**
```json
{
  "code": 200,
  "message": "薄弱知识点获取成功",
  "data": {
    "weakKnowledgePoints": [
      {
        "id": "hamilton",
        "name": "哈密顿图", 
        "currentScore": 65
      }
    ]
  }
}
```

## 错误处理规范

### HTTP状态码
- `200`: 成功
- `400`: 请求参数错误
- `401`: 未授权/token无效  
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

### 错误响应格式
```json
{
  "code": 400,
  "message": "具体错误信息",
  "data": null
}
```

## 前端启用真实API的步骤

1. **修改API地址**
   ```typescript
   // 在 src/api/student.ts 中修改
   const API_BASE_URL = 'http://your-backend-url:8080'
   ```

2. **启用API调用代码**
   
   - 打开 `src/api/student.ts`
   - 找到每个方法中的注释代码块
   - 取消注释真实API调用代码
   - 注释掉或删除模拟数据代码
   
3. **示例修改**
   
   ```typescript
   // 将这样的代码：
   /*
   // 真实API调用代码 - 后端开发时取消注释
   const response = await fetch(...)
   */
   
   // 改为：
   // 真实API调用代码
   const response = await fetch(...)
   ```
