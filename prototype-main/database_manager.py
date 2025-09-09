#!/usr/bin/env python3
"""
数据库管理工具
提供数据库的初始化、备份、恢复等功能
"""

import sqlite3
import json
import os
from datetime import datetime
from database import StudentDatabase

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path: str = "student_data.db"):
        self.db_path = db_path
        self.db = StudentDatabase(db_path)
    
    def backup_database(self, backup_path: str = None):
        """备份数据库"""
        if not backup_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"
        
        try:
            # 创建备份
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            
            print(f"✅ 数据库备份成功: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"❌ 数据库备份失败: {e}")
            return None
    
    def restore_database(self, backup_path: str):
        """恢复数据库"""
        if not os.path.exists(backup_path):
            print(f"❌ 备份文件不存在: {backup_path}")
            return False
        
        try:
            # 备份当前数据库
            current_backup = self.backup_database()
            
            # 恢复数据库
            with sqlite3.connect(backup_path) as source:
                with sqlite3.connect(self.db_path) as target:
                    source.backup(target)
            
            print(f"✅ 数据库恢复成功: {backup_path}")
            print(f"📁 当前数据库已备份为: {current_backup}")
            return True
        except Exception as e:
            print(f"❌ 数据库恢复失败: {e}")
            return False
    
    def export_student_data(self, student_id: str, export_path: str = None):
        """导出学生数据"""
        if not export_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = f"student_{student_id}_{timestamp}.json"
        
        try:
            # 获取学生数据
            mastery = self.db.get_student_mastery(student_id)
            stats = self.db.get_student_statistics(student_id)
            weak_points = self.db.get_weak_knowledge_points(student_id)
            learning_trend = self.db.get_learning_trend(student_id, 365)  # 一年数据
            recommendation_history = self.db.get_recommendation_history(student_id, 1000)
            
            # 组装数据
            export_data = {
                "studentId": student_id,
                "exportTime": datetime.now().isoformat(),
                "mastery": mastery,
                "statistics": stats,
                "weakKnowledgePoints": weak_points,
                "learningTrend": learning_trend,
                "recommendationHistory": recommendation_history
            }
            
            # 写入文件
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 学生数据导出成功: {export_path}")
            return export_path
        except Exception as e:
            print(f"❌ 学生数据导出失败: {e}")
            return None
    
    def get_database_stats(self):
        """获取数据库统计信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 学生数量
                cursor.execute("SELECT COUNT(*) FROM students")
                student_count = cursor.fetchone()[0]
                
                # 答题记录数量
                cursor.execute("SELECT COUNT(*) FROM answer_history")
                answer_count = cursor.fetchone()[0]
                
                # 推荐记录数量
                cursor.execute("SELECT COUNT(*) FROM recommendation_history")
                recommendation_count = cursor.fetchone()[0]
                
                # 知识点掌握度记录数量
                cursor.execute("SELECT COUNT(*) FROM knowledge_mastery")
                mastery_count = cursor.fetchone()[0]
                
                # 数据库文件大小
                db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                
                stats = {
                    "studentCount": student_count,
                    "answerCount": answer_count,
                    "recommendationCount": recommendation_count,
                    "masteryCount": mastery_count,
                    "databaseSize": db_size,
                    "databaseSizeMB": round(db_size / (1024 * 1024), 2)
                }
                
                return stats
        except Exception as e:
            print(f"❌ 获取数据库统计失败: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 90):
        """清理旧数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 清理旧的答题历史（保留最近90天）
                cursor.execute('''
                    DELETE FROM answer_history 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                deleted_answers = cursor.rowcount
                
                # 清理旧的推荐历史（保留最近90天）
                cursor.execute('''
                    DELETE FROM recommendation_history 
                    WHERE created_at < datetime('now', '-{} days')
                '''.format(days))
                deleted_recommendations = cursor.rowcount
                
                conn.commit()
                
                print(f"✅ 数据清理完成:")
                print(f"   - 删除答题记录: {deleted_answers}条")
                print(f"   - 删除推荐记录: {deleted_recommendations}条")
                
                return True
        except Exception as e:
            print(f"❌ 数据清理失败: {e}")
            return False
    
    def reset_student_data(self, student_id: str):
        """重置学生数据"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 删除学生相关数据
                cursor.execute("DELETE FROM answer_history WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM recommendation_history WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM knowledge_mastery WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM study_sessions WHERE student_id = ?", (student_id,))
                cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
                
                conn.commit()
                
                print(f"✅ 学生 {student_id} 数据重置成功")
                return True
        except Exception as e:
            print(f"❌ 学生数据重置失败: {e}")
            return False
    
    def list_all_students(self):
        """列出所有学生"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT s.student_id, s.username, s.total_questions, s.correct_answers,
                           s.created_at, s.last_login
                    FROM students s
                    ORDER BY s.last_login DESC
                ''')
                
                students = []
                for row in cursor.fetchall():
                    student_id, username, total_q, correct_q, created_at, last_login = row
                    accuracy = int((correct_q / total_q * 100)) if total_q > 0 else 0
                    
                    students.append({
                        "studentId": student_id,
                        "username": username,
                        "totalQuestions": total_q,
                        "accuracy": accuracy,
                        "createdAt": created_at,
                        "lastLogin": last_login
                    })
                
                return students
        except Exception as e:
            print(f"❌ 获取学生列表失败: {e}")
            return []
    
    def print_database_summary(self):
        """打印数据库摘要"""
        stats = self.get_database_stats()
        students = self.list_all_students()
        
        print("\n📊 数据库摘要")
        print("=" * 50)
        print(f"📁 数据库文件: {self.db_path}")
        print(f"💾 文件大小: {stats.get('databaseSizeMB', 0)} MB")
        print(f"👥 学生数量: {stats.get('studentCount', 0)}")
        print(f"📝 答题记录: {stats.get('answerCount', 0)}")
        print(f"🎯 推荐记录: {stats.get('recommendationCount', 0)}")
        print(f"📈 掌握度记录: {stats.get('masteryCount', 0)}")
        
        if students:
            print(f"\n👥 学生列表 (最近活跃):")
            for student in students[:5]:  # 显示前5个
                print(f"   - {student['username']}: {student['totalQuestions']}题, {student['accuracy']}%正确率")

def main():
    """主函数"""
    manager = DatabaseManager()
    
    print("🗄️ 数据库管理工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("1. 查看数据库摘要")
        print("2. 备份数据库")
        print("3. 恢复数据库")
        print("4. 导出学生数据")
        print("5. 清理旧数据")
        print("6. 重置学生数据")
        print("7. 列出所有学生")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-7): ").strip()
        
        if choice == "1":
            manager.print_database_summary()
        
        elif choice == "2":
            backup_path = manager.backup_database()
            if backup_path:
                print(f"备份文件: {backup_path}")
        
        elif choice == "3":
            backup_path = input("请输入备份文件路径: ").strip()
            manager.restore_database(backup_path)
        
        elif choice == "4":
            student_id = input("请输入学生ID: ").strip()
            export_path = manager.export_student_data(student_id)
            if export_path:
                print(f"导出文件: {export_path}")
        
        elif choice == "5":
            days = input("请输入保留天数 (默认90天): ").strip()
            days = int(days) if days.isdigit() else 90
            manager.cleanup_old_data(days)
        
        elif choice == "6":
            student_id = input("请输入要重置的学生ID: ").strip()
            confirm = input(f"确认重置学生 {student_id} 的所有数据? (y/N): ").strip().lower()
            if confirm == 'y':
                manager.reset_student_data(student_id)
        
        elif choice == "7":
            students = manager.list_all_students()
            if students:
                print(f"\n👥 所有学生 ({len(students)}个):")
                for student in students:
                    print(f"   - {student['username']}: {student['totalQuestions']}题, {student['accuracy']}%正确率")
            else:
                print("没有找到学生数据")
        
        elif choice == "0":
            print("👋 再见!")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == '__main__':
    main()
