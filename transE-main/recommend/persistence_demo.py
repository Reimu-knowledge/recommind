#!/usr/bin/env python3
"""
数据持久化功能演示 - 展示如何在B/S架构中进行数据存储和恢复
"""

from start import EducationRecommendationAPI
import json
import time

def persistence_demo():
    """数据持久化功能演示"""
    print("🚀 数据持久化功能演示开始")
    print("=" * 80)
    
    # 初始化API
    api = EducationRecommendationAPI()
    
    # ===== 1. 创建多个学生并进行学习 =====
    print("\n📝 步骤1: 创建学生并进行学习...")
    
    students_data = [
        ("student_001", {"K1": 0.3, "K2": 0.1, "K3": 0.2}),
        ("student_002", {"K1": 0.1, "K2": 0.3, "K3": 0.1}),
        ("student_003", {"K1": 0.2, "K2": 0.2, "K3": 0.3})
    ]
    
    for student_id, initial_mastery in students_data:
        print(f"\n👨‍🎓 创建学生: {student_id}")
        
        # 开始会话
        session_result = api.start_session(student_id, initial_mastery)
        if session_result["status"] == "success":
            print(f"   ✅ 学生创建成功")
            
            # 模拟学习过程
            for batch in range(2):  # 进行2个批次的学习
                questions_result = api.get_questions(2)
                if questions_result["status"] == "success":
                    # 模拟答题
                    answers = []
                    for q in questions_result["recommendations"]:
                        # 随机选择答案
                        import random
                        selected = random.choice(['A', 'B', 'C', 'D'])
                        answers.append({"qid": q["qid"], "selected": selected})
                    
                    # 提交答案
                    submit_result = api.submit_student_answers(answers)
                    if submit_result["status"] == "success":
                        print(f"   📊 完成批次 {batch + 1}")
        
        # 结束会话
        api.end_session()
    
    # ===== 2. 查看当前学生列表 =====
    print(f"\n📊 步骤2: 查看当前系统中的学生...")
    students_list = api.get_students_list()
    if students_list["status"] == "success":
        print(f"   总学生数: {students_list['total_count']}")
        for student_info in students_list["students"]:
            print(f"   - {student_info['student_id']}: "
                  f"批次{student_info['batch_count']}, "
                  f"题目{student_info['total_questions']}, "
                  f"掌握{student_info['mastered_knowledge_points']}个知识点")
    
    # ===== 3. 导出单个学生数据 =====
    print(f"\n💾 步骤3: 导出单个学生数据...")
    export_result = api.export_student_data("student_001")
    if export_result["status"] == "success":
        print(f"   ✅ 学生数据导出成功")
        print(f"   数据大小: {len(str(export_result['data']))} 字符")
        
        # 保存到文件
        save_result = api.save_student_to_file("student_001", "demo_student_001.json")
        if save_result["status"] == "success":
            print(f"   💾 数据已保存到文件: {save_result['file_path']}")
    
    # ===== 4. 导出所有学生数据 =====
    print(f"\n💾 步骤4: 导出所有学生数据...")
    export_all_result = api.export_all_students()
    if export_all_result["status"] == "success":
        print(f"   ✅ 所有学生数据导出成功")
        print(f"   学生数量: {export_all_result['student_count']}")
        
        # 保存到文件
        save_all_result = api.save_all_students_to_file("demo_all_students.json")
        if save_all_result["status"] == "success":
            print(f"   💾 数据已保存到文件: {save_all_result['file_path']}")
    
    # ===== 5. 清空所有学生数据（模拟服务重启） =====
    print(f"\n🔄 步骤5: 模拟服务重启（清空内存数据）...")
    clear_result = api.clear_all_students()
    if clear_result["status"] == "success":
        print(f"   ✅ 已清空 {clear_result['cleared_count']} 个学生的数据")
    
    # 验证数据已清空
    empty_list = api.get_students_list()
    print(f"   📊 当前学生数: {empty_list['total_count']}")
    
    # ===== 6. 从文件恢复所有学生数据 =====
    print(f"\n🔄 步骤6: 从文件恢复所有学生数据...")
    load_result = api.load_all_students_from_file("demo_all_students.json")
    if load_result["status"] == "success":
        print(f"   ✅ 数据恢复成功")
        print(f"   成功恢复: {load_result['success_count']} 个学生")
        print(f"   失败: {load_result['error_count']} 个学生")
    
    # 验证数据已恢复
    restored_list = api.get_students_list()
    if restored_list["status"] == "success":
        print(f"   📊 恢复后学生数: {restored_list['total_count']}")
        for student_info in restored_list["students"]:
            print(f"   - {student_info['student_id']}: "
                  f"批次{student_info['batch_count']}, "
                  f"题目{student_info['total_questions']}")
    
    # ===== 7. 测试单个学生数据恢复 =====
    print(f"\n🔄 步骤7: 测试单个学生数据恢复...")
    
    # 先清空数据
    api.clear_all_students()
    
    # 从文件恢复单个学生
    load_single_result = api.load_student_from_file("demo_student_001.json")
    if load_single_result["status"] == "success":
        print(f"   ✅ 单个学生数据恢复成功")
        print(f"   学生ID: {load_single_result['student_id']}")
        print(f"   批次数: {load_single_result['batch_count']}")
        print(f"   题目数: {load_single_result['total_questions']}")
    
    # ===== 8. 测试与现有API的兼容性 =====
    print(f"\n🧪 步骤8: 测试恢复后的学生能否正常使用...")
    
    # 开始已存在学生的会话
    api.current_session = "student_001"
    status_result = api.get_session_status()
    if status_result["status"] == "success":
        print(f"   ✅ 恢复的学生状态正常")
        print(f"   当前掌握度: {len(status_result['mastered_knowledge_points'])} 个知识点")
        
        # 获取推荐题目
        questions_result = api.get_questions(1)
        if questions_result["status"] == "success":
            print(f"   ✅ 推荐系统正常工作")
            print(f"   推荐了 {len(questions_result['recommendations'])} 道题目")
    
    api.end_session()
    
    print(f"\n🎉 数据持久化功能演示完成！")
    print("=" * 80)
    print("📋 演示结果总结:")
    print("   ✅ 单个学生数据导出/导入")
    print("   ✅ 批量学生数据导出/导入")
    print("   ✅ 文件持久化存储")
    print("   ✅ 服务重启后数据恢复")
    print("   ✅ 与现有API完全兼容")
    print("\n💡 B/S架构集成建议:")
    print("   1. 定期调用 export_all_students() 导出数据到数据库")
    print("   2. 服务启动时调用 import_all_students() 恢复数据")
    print("   3. 关键时刻调用 save_student_to_file() 备份重要学生数据")
    print("   4. 使用 get_students_list() 监控系统中的学生状态")

def database_integration_example():
    """数据库集成示例代码"""
    print(f"\n" + "=" * 80)
    print("📖 数据库集成示例代码")
    print("=" * 80)
    
    print("""
# 示例：与数据库集成的前端服务代码

from start import EducationRecommendationAPI
import mysql.connector  # 或其他数据库连接库
import json

class StudentDataManager:
    def __init__(self):
        self.api = EducationRecommendationAPI()
        self.db_connection = mysql.connector.connect(
            host='localhost',
            user='username',
            password='password',
            database='education_system'
        )
    
    def save_student_to_database(self, student_id):
        \"\"\"将学生数据保存到数据库\"\"\"
        # 1. 从推荐系统导出数据
        export_result = self.api.export_student_data(student_id)
        if export_result["status"] == "success":
            student_data = export_result["data"]
            
            # 2. 保存到数据库
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO student_data (student_id, data, updated_at) 
                VALUES (%s, %s, NOW())
                ON DUPLICATE KEY UPDATE 
                data = VALUES(data), updated_at = NOW()
            ''', (student_id, json.dumps(student_data)))
            
            self.db_connection.commit()
            return True
        return False
    
    def load_student_from_database(self, student_id):
        \"\"\"从数据库恢复学生数据\"\"\"
        cursor = self.db_connection.cursor()
        cursor.execute(
            'SELECT data FROM student_data WHERE student_id = %s', 
            (student_id,)
        )
        
        result = cursor.fetchone()
        if result:
            student_data = json.loads(result[0])
            
            # 导入到推荐系统
            import_result = self.api.import_student_data(student_data)
            return import_result["status"] == "success"
        return False
    
    def backup_all_students(self):
        \"\"\"备份所有学生数据\"\"\"
        export_result = self.api.export_all_students()
        if export_result["status"] == "success":
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO system_backups (backup_data, created_at)
                VALUES (%s, NOW())
            ''', (json.dumps(export_result["data"]),))
            
            self.db_connection.commit()
            return True
        return False
    
    def restore_from_backup(self, backup_id=None):
        \"\"\"从备份恢复系统数据\"\"\"
        cursor = self.db_connection.cursor()
        if backup_id:
            cursor.execute(
                'SELECT backup_data FROM system_backups WHERE id = %s', 
                (backup_id,)
            )
        else:
            cursor.execute(
                'SELECT backup_data FROM system_backups ORDER BY created_at DESC LIMIT 1'
            )
        
        result = cursor.fetchone()
        if result:
            backup_data = json.loads(result[0])
            import_result = self.api.import_all_students(backup_data)
            return import_result["status"] in ["success", "partial"]
        return False

# 使用示例
data_manager = StudentDataManager()

# 定期备份（可以设置定时任务）
data_manager.backup_all_students()

# 服务启动时恢复数据
data_manager.restore_from_backup()

# 学生学习过程中实时保存
data_manager.save_student_to_database("student_001")
    """)

if __name__ == "__main__":
    try:
        persistence_demo()
        database_integration_example()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
