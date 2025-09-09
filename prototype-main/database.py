#!/usr/bin/env python3
"""
学生数据库管理模块
提供学生学习数据的持久化存储和管理功能
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class StudentDatabase:
    """学生数据库管理类"""
    
    def __init__(self, db_path: str = "student_data.db"):
        """初始化数据库"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库表结构"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 学生基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    total_questions INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    study_time_minutes INTEGER DEFAULT 0
                )
            ''')
            
            # 知识点掌握度表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge_mastery (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    knowledge_point TEXT NOT NULL,
                    mastery_score REAL DEFAULT 0.0,
                    practice_count INTEGER DEFAULT 0,
                    correct_count INTEGER DEFAULT 0,
                    last_practice TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (student_id),
                    UNIQUE(student_id, knowledge_point)
                )
            ''')
            
            # 答题历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS answer_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    selected_option TEXT NOT NULL,
                    is_correct BOOLEAN NOT NULL,
                    knowledge_point TEXT NOT NULL,
                    difficulty REAL DEFAULT 0.5,
                    response_time_seconds INTEGER DEFAULT 0,
                    batch_number INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            
            # 学习会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS study_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_end TIMESTAMP,
                    questions_answered INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    session_score REAL DEFAULT 0.0,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            
            # 推荐历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recommendation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    recommendation_reason TEXT,
                    was_answered BOOLEAN DEFAULT FALSE,
                    was_correct BOOLEAN,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES students (student_id)
                )
            ''')
            
            conn.commit()
            print("✅ 数据库初始化完成")
    
    def create_student(self, student_id: str, username: str, email: str = None) -> bool:
        """创建新学生记录"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO students (student_id, username, email, last_login)
                    VALUES (?, ?, ?, ?)
                ''', (student_id, username, email, datetime.now()))
                
                # 初始化知识点掌握度
                knowledge_points = ["K1", "K2", "K3", "K8"]
                for kp in knowledge_points:
                    cursor.execute('''
                        INSERT OR IGNORE INTO knowledge_mastery 
                        (student_id, knowledge_point, mastery_score)
                        VALUES (?, ?, ?)
                    ''', (student_id, kp, 0.1))  # 初始掌握度0.1
                
                conn.commit()
                print(f"✅ 学生 {username} 创建成功")
                return True
        except Exception as e:
            print(f"❌ 创建学生失败: {e}")
            return False
    
    def get_student_mastery(self, student_id: str) -> Dict[str, float]:
        """获取学生知识点掌握度"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT knowledge_point, mastery_score 
                    FROM knowledge_mastery 
                    WHERE student_id = ?
                ''', (student_id,))
                
                mastery = {row[0]: row[1] for row in cursor.fetchall()}
                return mastery
        except Exception as e:
            print(f"❌ 获取掌握度失败: {e}")
            return {}
    
    def update_mastery(self, student_id: str, knowledge_point: str, 
                      is_correct: bool, difficulty: float = 0.5) -> bool:
        """更新知识点掌握度"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取当前掌握度
                cursor.execute('''
                    SELECT mastery_score, practice_count, correct_count
                    FROM knowledge_mastery 
                    WHERE student_id = ? AND knowledge_point = ?
                ''', (student_id, knowledge_point))
                
                result = cursor.fetchone()
                if result:
                    current_score, practice_count, correct_count = result
                else:
                    current_score, practice_count, correct_count = 0.1, 0, 0
                
                # 计算新的掌握度
                if is_correct:
                    # 答对：掌握度提升，提升幅度与难度成反比
                    improvement = 0.2 * (1 - difficulty * 0.5)  # 难度越高，提升越少
                    new_score = min(1.0, current_score + improvement)
                    correct_count += 1
                else:
                    # 答错：掌握度轻微下降，但不会低于0.05
                    penalty = 0.05 * difficulty
                    new_score = max(0.05, current_score - penalty)
                
                practice_count += 1
                
                # 更新数据库
                cursor.execute('''
                    INSERT OR REPLACE INTO knowledge_mastery 
                    (student_id, knowledge_point, mastery_score, practice_count, 
                     correct_count, last_practice, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, knowledge_point, new_score, practice_count, 
                      correct_count, datetime.now(), datetime.now()))
                
                conn.commit()
                print(f"📊 更新掌握度: {knowledge_point} = {new_score:.3f}")
                return True
        except Exception as e:
            print(f"❌ 更新掌握度失败: {e}")
            return False
    
    def record_answer(self, student_id: str, question_id: str, selected_option: str,
                     is_correct: bool, knowledge_point: str, difficulty: float = 0.5,
                     response_time: int = 0, batch_number: int = 1) -> bool:
        """记录答题历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO answer_history 
                    (student_id, question_id, selected_option, is_correct, 
                     knowledge_point, difficulty, response_time_seconds, batch_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (student_id, question_id, selected_option, is_correct,
                      knowledge_point, difficulty, response_time, batch_number))
                
                # 更新学生统计
                cursor.execute('''
                    UPDATE students 
                    SET total_questions = total_questions + 1,
                        correct_answers = correct_answers + ?,
                        last_login = ?
                    WHERE student_id = ?
                ''', (1 if is_correct else 0, datetime.now(), student_id))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ 记录答题历史失败: {e}")
            return False
    
    def get_weak_knowledge_points(self, student_id: str, threshold: float = 0.5) -> List[Dict]:
        """获取薄弱知识点"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT km.knowledge_point, km.mastery_score, km.practice_count, km.correct_count
                    FROM knowledge_mastery km
                    WHERE km.student_id = ? AND km.mastery_score < ?
                    ORDER BY km.mastery_score ASC
                ''', (student_id, threshold))
                
                weak_points = []
                for row in cursor.fetchall():
                    kp, score, practice_count, correct_count = row
                    weak_points.append({
                        "id": kp,
                        "name": self._get_knowledge_point_name(kp),
                        "currentScore": int(score * 100),
                        "practiceCount": practice_count,
                        "correctCount": correct_count,
                        "accuracy": int((correct_count / practice_count * 100)) if practice_count > 0 else 0
                    })
                
                return weak_points
        except Exception as e:
            print(f"❌ 获取薄弱知识点失败: {e}")
            return []
    
    def get_student_statistics(self, student_id: str) -> Dict:
        """获取学生学习统计"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 获取基本信息
                cursor.execute('''
                    SELECT total_questions, correct_answers, study_time_minutes
                    FROM students WHERE student_id = ?
                ''', (student_id,))
                
                student_info = cursor.fetchone()
                if not student_info:
                    return {}
                
                total_questions, correct_answers, study_time = student_info
                
                # 获取知识点统计
                cursor.execute('''
                    SELECT COUNT(*) as total_kp,
                           AVG(mastery_score) as avg_mastery,
                           SUM(practice_count) as total_practice
                    FROM knowledge_mastery WHERE student_id = ?
                ''', (student_id,))
                
                kp_stats = cursor.fetchone()
                
                # 获取最近答题情况
                cursor.execute('''
                    SELECT COUNT(*) as recent_questions,
                           SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as recent_correct
                    FROM answer_history 
                    WHERE student_id = ? AND created_at >= datetime('now', '-7 days')
                ''', (student_id,))
                
                recent_stats = cursor.fetchone()
                
                return {
                    "totalQuestions": total_questions or 0,
                    "correctAnswers": correct_answers or 0,
                    "accuracy": int((correct_answers / total_questions * 100)) if total_questions > 0 else 0,
                    "studyTimeMinutes": study_time or 0,
                    "totalKnowledgePoints": kp_stats[0] or 0,
                    "averageMastery": round(kp_stats[1] * 100, 1) if kp_stats[1] else 0,
                    "totalPractice": kp_stats[2] or 0,
                    "recentQuestions": recent_stats[0] or 0,
                    "recentAccuracy": int((recent_stats[1] / recent_stats[0] * 100)) if recent_stats[0] > 0 else 0
                }
        except Exception as e:
            print(f"❌ 获取学习统计失败: {e}")
            return {}
    
    def get_recommendation_history(self, student_id: str, limit: int = 10) -> List[Dict]:
        """获取推荐历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT question_id, recommendation_reason, was_answered, was_correct, created_at
                    FROM recommendation_history 
                    WHERE student_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                ''', (student_id, limit))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        "questionId": row[0],
                        "reason": row[1],
                        "wasAnswered": bool(row[2]),
                        "wasCorrect": bool(row[3]) if row[3] is not None else None,
                        "createdAt": row[4]
                    })
                
                return history
        except Exception as e:
            print(f"❌ 获取推荐历史失败: {e}")
            return []
    
    def record_recommendation(self, student_id: str, question_id: str, reason: str) -> bool:
        """记录推荐历史"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO recommendation_history 
                    (student_id, question_id, recommendation_reason)
                    VALUES (?, ?, ?)
                ''', (student_id, question_id, reason))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ 记录推荐历史失败: {e}")
            return False
    
    def update_recommendation_result(self, student_id: str, question_id: str, was_correct: bool) -> bool:
        """更新推荐结果"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE recommendation_history 
                    SET was_answered = TRUE, was_correct = ?
                    WHERE student_id = ? AND question_id = ? 
                    AND created_at = (SELECT MAX(created_at) FROM recommendation_history 
                                    WHERE student_id = ? AND question_id = ?)
                ''', (was_correct, student_id, question_id, student_id, question_id))
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ 更新推荐结果失败: {e}")
            return False
    
    def _get_knowledge_point_name(self, kp_id: str) -> str:
        """获取知识点名称"""
        names = {
            "K1": "集合运算",
            "K2": "关系映射", 
            "K3": "图基本概念",
            "K8": "度的概念"
        }
        return names.get(kp_id, "未知知识点")
    
    def get_learning_trend(self, student_id: str, days: int = 7) -> List[Dict]:
        """获取学习趋势"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DATE(created_at) as date,
                           COUNT(*) as questions,
                           SUM(CASE WHEN is_correct THEN 1 ELSE 0 END) as correct
                    FROM answer_history 
                    WHERE student_id = ? AND created_at >= datetime('now', '-{} days')
                    GROUP BY DATE(created_at)
                    ORDER BY date ASC
                '''.format(days), (student_id,))
                
                trend = []
                for row in cursor.fetchall():
                    trend.append({
                        "date": row[0],
                        "questions": row[1],
                        "correct": row[2],
                        "accuracy": int((row[2] / row[1] * 100)) if row[1] > 0 else 0
                    })
                
                return trend
        except Exception as e:
            print(f"❌ 获取学习趋势失败: {e}")
            return []

# 全局数据库实例
db = StudentDatabase()
