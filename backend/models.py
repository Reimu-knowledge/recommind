#!/usr/bin/env python3
"""
数据库模型定义
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Student(db.Model):
    """学生信息表"""
    __tablename__ = 'students'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    grade = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # 关联关系
    learning_sessions = db.relationship('LearningSession', backref='student', lazy=True, cascade='all, delete-orphan')
    knowledge_mastery = db.relationship('KnowledgeMastery', backref='student', lazy=True, cascade='all, delete-orphan')
    answer_records = db.relationship('AnswerRecord', backref='student', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'grade': self.grade,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }

class LearningSession(db.Model):
    """学习会话表"""
    __tablename__ = 'learning_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    session_name = db.Column(db.String(100), nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    total_questions = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_name': self.session_name,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'accuracy': self.accuracy,
            'is_active': self.is_active
        }

class KnowledgeMastery(db.Model):
    """知识点掌握度表"""
    __tablename__ = 'knowledge_mastery'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    knowledge_point_id = db.Column(db.String(20), nullable=False)  # K1, K2, etc.
    mastery_score = db.Column(db.Float, default=0.0)  # 0.0 - 1.0
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    practice_count = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    
    # 复合唯一索引
    __table_args__ = (db.UniqueConstraint('student_id', 'knowledge_point_id'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'knowledge_point_id': self.knowledge_point_id,
            'mastery_score': self.mastery_score,
            'last_updated': self.last_updated.isoformat(),
            'practice_count': self.practice_count,
            'correct_count': self.correct_count
        }

class AnswerRecord(db.Model):
    """答题记录表"""
    __tablename__ = 'answer_records'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('learning_sessions.id'), nullable=True)
    question_id = db.Column(db.String(20), nullable=False)  # Q1, Q2, etc.
    selected_answer = db.Column(db.String(10), nullable=False)  # A, B, C, D
    correct_answer = db.Column(db.String(10), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    knowledge_points = db.Column(db.Text, nullable=False)  # JSON字符串
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'selected_answer': self.selected_answer,
            'correct_answer': self.correct_answer,
            'is_correct': self.is_correct,
            'knowledge_points': json.loads(self.knowledge_points),
            'answered_at': self.answered_at.isoformat()
        }

class QuestionBank(db.Model):
    """题库表"""
    __tablename__ = 'question_bank'
    
    id = db.Column(db.String(20), primary_key=True)  # Q1, Q2, etc.
    content = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # JSON字符串
    correct_answer = db.Column(db.String(10), nullable=False)
    knowledge_points = db.Column(db.Text, nullable=False)  # JSON字符串
    difficulty = db.Column(db.Float, default=0.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'options': json.loads(self.options),
            'correct_answer': self.correct_answer,
            'knowledge_points': json.loads(self.knowledge_points),
            'difficulty': self.difficulty,
            'created_at': self.created_at.isoformat()
        }

class LearningProgress(db.Model):
    """学习进度表"""
    __tablename__ = 'learning_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(50), db.ForeignKey('students.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    accuracy = db.Column(db.Float, default=0.0)
    study_time_minutes = db.Column(db.Integer, default=0)
    
    # 复合唯一索引
    __table_args__ = (db.UniqueConstraint('student_id', 'date'),)
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'date': self.date.isoformat(),
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy': self.accuracy,
            'study_time_minutes': self.study_time_minutes
        }
