# 数据持久化API参考文档

## 🎯 B/S架构数据持久化解决方案

本文档描述了为支持B/S架构而新增的数据持久化API，使前端开发人员能够完整地实现学生数据的存储和恢复。

## 📋 新增API列表

### 1. 学生数据导出/导入

#### `export_student_data(student_id: str = None) -> Dict`
导出指定学生的完整数据用于持久化存储。

**参数:**
- `student_id`: 学生ID，如果不提供则使用当前会话的学生

**返回:**
```json
{
    "status": "success",
    "student_id": "student_001",
    "data": {
        "student_id": "student_001",
        "embedding_dim": 50,
        "mastery_scores": {...},
        "question_history": [...],
        "batch_count": 2,
        "vector": [...],
        "vector_history": [...],
        "export_timestamp": 1725544234.567,
        "version": "1.1"
    },
    "export_timestamp": 1725544234.567,
    "message": "学生 student_001 数据导出成功"
}
```

#### `import_student_data(student_data: Dict) -> Dict`
从持久化数据恢复学生对象。

**参数:**
- `student_data`: 通过`export_student_data`导出的数据

**返回:**
```json
{
    "status": "success",
    "student_id": "student_001",
    "batch_count": 2,
    "total_questions": 4,
    "message": "学生 student_001 数据恢复成功"
}
```

### 2. 批量数据管理

#### `export_all_students() -> Dict`
导出所有学生数据。

**返回:**
```json
{
    "status": "success",
    "data": {
        "student_001": {...},
        "student_002": {...},
        "student_003": {...}
    },
    "student_count": 3,
    "export_timestamp": 1725544234.567,
    "message": "成功导出 3 个学生的数据"
}
```

#### `import_all_students(students_data: Dict) -> Dict`
批量恢复学生数据。

**参数:**
- `students_data`: 通过`export_all_students`导出的数据

**返回:**
```json
{
    "status": "success",
    "success_count": 3,
    "error_count": 0,
    "errors": [],
    "message": "成功恢复 3 个学生，失败 0 个"
}
```

### 3. 文件持久化

#### `save_student_to_file(student_id: str = None, file_path: str = None) -> Dict`
将学生数据保存到JSON文件。

**参数:**
- `student_id`: 学生ID
- `file_path`: 文件路径，如果不提供则自动生成

**返回:**
```json
{
    "status": "success",
    "student_id": "student_001",
    "file_path": "student_data_student_001_1725544234.json",
    "message": "学生 student_001 数据已保存到 student_data_student_001_1725544234.json"
}
```

#### `load_student_from_file(file_path: str) -> Dict`
从JSON文件加载学生数据。

#### `save_all_students_to_file(file_path: str = None) -> Dict`
将所有学生数据保存到JSON文件。

#### `load_all_students_from_file(file_path: str) -> Dict`
从JSON文件加载所有学生数据。

### 4. 系统管理

#### `get_students_list() -> Dict`
获取当前系统中所有学生的基本信息。

**返回:**
```json
{
    "status": "success",
    "students": [
        {
            "student_id": "student_001",
            "batch_count": 2,
            "total_questions": 4,
            "mastered_knowledge_points": 0,
            "average_mastery": 0.234,
            "last_activity": 1725544234.567
        }
    ],
    "total_count": 1,
    "message": "当前系统中有 1 个学生"
}
```

#### `clear_all_students() -> Dict`
清空所有学生数据（谨慎使用）。

**返回:**
```json
{
    "status": "success",
    "cleared_count": 3,
    "message": "已清空 3 个学生的数据"
}
```

## 🔧 B/S架构集成方案

### 方案1: 定时备份策略

```python
from start import EducationRecommendationAPI
import schedule
import time

api = EducationRecommendationAPI()

def backup_to_database():
    """定时备份到数据库"""
    export_result = api.export_all_students()
    if export_result["status"] == "success":
        # 保存到数据库的代码
        save_to_database(export_result["data"])

# 每30分钟备份一次
schedule.every(30).minutes.do(backup_to_database)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### 方案2: 实时同步策略

```python
class RealtimeDataManager:
    def __init__(self):
        self.api = EducationRecommendationAPI()
    
    def on_student_answer_submitted(self, student_id):
        """学生答题后实时备份"""
        export_result = self.api.export_student_data(student_id)
        if export_result["status"] == "success":
            # 立即保存到数据库
            save_student_to_database(student_id, export_result["data"])
    
    def on_session_ended(self, student_id):
        """会话结束后备份"""
        self.on_student_answer_submitted(student_id)
```

### 方案3: 服务启动恢复

```python
class ServiceInitializer:
    def __init__(self):
        self.api = EducationRecommendationAPI()
    
    def restore_all_students_on_startup(self):
        """服务启动时恢复所有学生数据"""
        # 从数据库获取最新备份
        latest_backup = get_latest_backup_from_database()
        
        if latest_backup:
            import_result = self.api.import_all_students(latest_backup)
            if import_result["status"] == "success":
                print(f"成功恢复 {import_result['success_count']} 个学生")
            else:
                print(f"数据恢复失败: {import_result['message']}")
```

## 📊 数据库表设计建议

### 学生数据表
```sql
CREATE TABLE student_data (
    student_id VARCHAR(255) PRIMARY KEY,
    data JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_updated_at (updated_at)
);
```

### 系统备份表
```sql
CREATE TABLE system_backups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_data JSON NOT NULL,
    student_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);
```

## 🔄 数据版本兼容性

当前数据格式版本为`1.1`，包含以下字段：

### 必要字段
- `student_id`: 学生唯一标识
- `mastery_scores`: 知识点掌握度字典
- `question_history`: 答题历史列表
- `batch_count`: 批次计数

### 可选字段
- `vector`: 学生向量表示
- `vector_history`: 向量历史
- `embedding_dim`: 向量维度
- `export_timestamp`: 导出时间戳
- `version`: 数据格式版本

### 向后兼容性
系统支持导入较旧版本的数据，缺失的字段会使用默认值填充。

## ⚠️ 注意事项

1. **数据安全**: 学生数据包含学习隐私，需要加密存储
2. **并发访问**: 多个进程同时操作时需要考虑数据一致性
3. **存储大小**: 向量数据较大，建议定期清理历史数据
4. **备份频率**: 根据业务需求调整备份频率，避免性能影响
5. **恢复测试**: 定期测试数据恢复流程，确保备份有效

## 📈 性能优化建议

1. **增量备份**: 只备份有变化的学生数据
2. **压缩存储**: 对JSON数据进行压缩存储
3. **异步处理**: 使用异步任务处理数据备份
4. **缓存策略**: 对频繁访问的学生数据进行缓存
5. **分片存储**: 大量学生时考虑分片存储

## 🎯 最佳实践

1. **定期备份**: 每30分钟或每次学习会话结束后备份
2. **多重备份**: 同时使用数据库和文件备份
3. **监控告警**: 监控备份成功率，失败时及时告警
4. **数据验证**: 恢复数据后验证完整性
5. **版本管理**: 保留多个版本的备份数据

---

**总结**: 通过这些API，前端开发人员可以完全独立地实现B/S架构下的数据持久化，无需修改推荐算法核心代码，完美支持分布式部署和数据恢复。
