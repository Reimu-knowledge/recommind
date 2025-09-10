#!/usr/bin/env python3
"""
业务逻辑服务层
"""

import json
import os
import sys
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import logging

# 添加recommend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'recommend'))

from models import db, Student, LearningSession, KnowledgeMastery, AnswerRecord, QuestionBank, LearningProgress

logger = logging.getLogger(__name__)

class StudentService:
    """学生管理服务"""
    
    @staticmethod
    def create_student(student_data: Dict) -> Tuple[bool, str, Optional[Student]]:
        """创建新学生"""
        try:
            # 检查学生是否已存在
            existing_student = Student.query.filter_by(id=student_data['id']).first()
            if existing_student:
                return False, f"学生ID {student_data['id']} 已存在", None
            
            # 创建新学生
            student = Student(
                id=student_data['id'],
                name=student_data['name'],
                email=student_data.get('email'),
                grade=student_data.get('grade')
            )
            
            db.session.add(student)
            db.session.commit()
            
            logger.info(f"创建新学生: {student_data['id']}")
            return True, "学生创建成功", student
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"创建学生失败: {e}")
            return False, f"创建学生失败: {str(e)}", None
    
    @staticmethod
    def get_student_with_stats(student_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """获取学生信息及学习统计"""
        try:
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return False, f"学生 {student_id} 不存在", None
            
            # 获取学习统计
            total_sessions = LearningSession.query.filter_by(student_id=student_id).count()
            active_sessions = LearningSession.query.filter_by(student_id=student_id, is_active=True).count()
            total_questions = AnswerRecord.query.filter_by(student_id=student_id).count()
            correct_answers = AnswerRecord.query.filter_by(student_id=student_id, is_correct=True).count()
            
            student_data = student.to_dict()
            student_data.update({
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'overall_accuracy': correct_answers / total_questions if total_questions > 0 else 0
            })
            
            return True, "获取成功", student_data
            
        except Exception as e:
            logger.error(f"获取学生信息失败: {e}")
            return False, f"获取学生信息失败: {str(e)}", None
    
    @staticmethod
    def get_all_students(page: int = 1, per_page: int = 20) -> Tuple[bool, str, Optional[Dict]]:
        """获取所有学生列表"""
        try:
            students = Student.query.filter_by(is_active=True).paginate(
                page=page, per_page=per_page, error_out=False
            )
            
            student_list = []
            for student in students.items:
                student_data = student.to_dict()
                # 添加学习统计
                total_questions = AnswerRecord.query.filter_by(student_id=student.id).count()
                correct_answers = AnswerRecord.query.filter_by(student_id=student.id, is_correct=True).count()
                student_data['overall_accuracy'] = correct_answers / total_questions if total_questions > 0 else 0
                student_list.append(student_data)
            
            result = {
                'students': student_list,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': students.total,
                    'pages': students.pages,
                    'has_next': students.has_next,
                    'has_prev': students.has_prev
                }
            }
            
            return True, "获取成功", result
            
        except Exception as e:
            logger.error(f"获取学生列表失败: {e}")
            return False, f"获取学生列表失败: {str(e)}", None

class LearningSessionService:
    """学习会话服务"""
    
    @staticmethod
    def start_session(student_id: str, session_name: Optional[str] = None) -> Tuple[bool, str, Optional[LearningSession]]:
        """开始学习会话"""
        try:
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return False, f"学生 {student_id} 不存在", None
            
            if not session_name:
                session_name = f"学习会话_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 创建学习会话
            session = LearningSession(
                student_id=student_id,
                session_name=session_name
            )
            
            db.session.add(session)
            db.session.commit()
            
            logger.info(f"学生 {student_id} 开始学习会话: {session.id}")
            return True, "学习会话开始成功", session
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"开始学习会话失败: {e}")
            return False, f"开始学习会话失败: {str(e)}", None
    
    @staticmethod
    def end_session(session_id: int) -> Tuple[bool, str, Optional[LearningSession]]:
        """结束学习会话"""
        try:
            session = LearningSession.query.get(session_id)
            if not session:
                return False, f"学习会话 {session_id} 不存在", None
            
            if not session.is_active:
                return False, f"学习会话 {session_id} 已经结束", None
            
            # 结束会话
            session.ended_at = datetime.utcnow()
            session.is_active = False
            
            # 计算准确率
            if session.total_questions > 0:
                session.accuracy = session.correct_answers / session.total_questions
            
            db.session.commit()
            
            logger.info(f"学习会话 {session_id} 结束")
            return True, "学习会话结束成功", session
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"结束学习会话失败: {e}")
            return False, f"结束学习会话失败: {str(e)}", None

class KnowledgeMasteryService:
    """知识点掌握度服务"""
    
    @staticmethod
    def update_mastery(student_id: str, mastery_data: Dict[str, float]) -> Tuple[bool, str]:
        """更新知识点掌握度"""
        try:
            for kp_id, mastery_score in mastery_data.items():
                mastery_record = KnowledgeMastery.query.filter_by(
                    student_id=student_id,
                    knowledge_point_id=kp_id
                ).first()
                
                if mastery_record:
                    mastery_record.mastery_score = mastery_score
                    mastery_record.last_updated = datetime.utcnow()
                else:
                    mastery_record = KnowledgeMastery(
                        student_id=student_id,
                        knowledge_point_id=kp_id,
                        mastery_score=mastery_score
                    )
                    db.session.add(mastery_record)
            
            db.session.commit()
            return True, "知识点掌握度更新成功"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新知识点掌握度失败: {e}")
            return False, f"更新知识点掌握度失败: {str(e)}"
    
    @staticmethod
    def get_mastery_summary(student_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """获取学生知识点掌握情况摘要"""
        try:
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return False, f"学生 {student_id} 不存在", None
            
            mastery_records = KnowledgeMastery.query.filter_by(student_id=student_id).all()
            
            mastery_data = {}
            total_points = len(mastery_records)
            mastered_points = 0
            
            for record in mastery_records:
                mastery_data[record.knowledge_point_id] = {
                    'mastery_score': record.mastery_score,
                    'last_updated': record.last_updated.isoformat(),
                    'practice_count': record.practice_count,
                    'correct_count': record.correct_count,
                    'accuracy': record.correct_count / record.practice_count if record.practice_count > 0 else 0
                }
                
                if record.mastery_score >= 0.5:
                    mastered_points += 1
            
            result = {
                'student_id': student_id,
                'knowledge_mastery': mastery_data,
                'total_knowledge_points': total_points,
                'mastered_points': mastered_points,
                'mastery_rate': mastered_points / total_points if total_points > 0 else 0
            }
            
            return True, "获取成功", result
            
        except Exception as e:
            logger.error(f"获取知识点掌握情况失败: {e}")
            return False, f"获取知识点掌握情况失败: {str(e)}", None

class AnswerRecordService:
    """答题记录服务"""
    
    @staticmethod
    def save_answer_records(student_id: str, session_id: Optional[int], answer_details: List[Dict]) -> Tuple[bool, str]:
        """保存答题记录"""
        try:
            session = None
            if session_id:
                session = LearningSession.query.get(session_id)
            
            for answer_detail in answer_details:
                # 保存答题记录
                answer_record = AnswerRecord(
                    student_id=student_id,
                    session_id=session_id,
                    question_id=answer_detail['qid'],
                    selected_answer=answer_detail['selected'],
                    correct_answer=answer_detail['correct_answer'],
                    is_correct=answer_detail['correct'],
                    knowledge_points=json.dumps(answer_detail['knowledge_points'])
                )
                db.session.add(answer_record)
                
                # 更新会话统计
                if session:
                    session.total_questions += 1
                    if answer_detail['correct']:
                        session.correct_answers += 1
                
                # 更新知识点练习统计
                for kp_id in answer_detail['knowledge_points'].keys():
                    mastery_record = KnowledgeMastery.query.filter_by(
                        student_id=student_id,
                        knowledge_point_id=kp_id
                    ).first()
                    
                    if mastery_record:
                        mastery_record.practice_count += 1
                        if answer_detail['correct']:
                            mastery_record.correct_count += 1
                    else:
                        mastery_record = KnowledgeMastery(
                            student_id=student_id,
                            knowledge_point_id=kp_id,
                            practice_count=1,
                            correct_count=1 if answer_detail['correct'] else 0
                        )
                        db.session.add(mastery_record)
            
            db.session.commit()
            return True, "答题记录保存成功"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"保存答题记录失败: {e}")
            return False, f"保存答题记录失败: {str(e)}"
    
    @staticmethod
    def get_learning_history(student_id: str, page: int = 1, per_page: int = 50) -> Tuple[bool, str, Optional[Dict]]:
        """获取学生学习历史"""
        try:
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return False, f"学生 {student_id} 不存在", None
            
            # 获取答题记录
            answer_records = AnswerRecord.query.filter_by(student_id=student_id).order_by(
                AnswerRecord.answered_at.desc()
            ).paginate(page=page, per_page=per_page, error_out=False)
            
            # 获取学习会话
            sessions = LearningSession.query.filter_by(student_id=student_id).order_by(
                LearningSession.started_at.desc()
            ).all()
            
            result = {
                'answer_records': [record.to_dict() for record in answer_records.items],
                'sessions': [session.to_dict() for session in sessions],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': answer_records.total,
                    'pages': answer_records.pages,
                    'has_next': answer_records.has_next,
                    'has_prev': answer_records.has_prev
                }
            }
            
            return True, "获取成功", result
            
        except Exception as e:
            logger.error(f"获取学习历史失败: {e}")
            return False, f"获取学习历史失败: {str(e)}", None

class QuestionBankService:
    """题库服务"""
    
    @staticmethod
    def import_questions_from_json(json_path: str) -> Tuple[bool, str, int]:
        """从JSON文件导入题目到数据库"""
        try:
            if not os.path.exists(json_path):
                return False, f"题目文件不存在: {json_path}", 0
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            questions = data.get('questions', [])
            imported_count = 0
            
            for q in questions:
                # 检查题目是否已存在
                existing_question = QuestionBank.query.get(q['qid'])
                if existing_question:
                    continue
                
                question = QuestionBank(
                    id=q['qid'],
                    content=q['content'],
                    options=json.dumps(q['options']),
                    correct_answer=q['answer'],
                    knowledge_points=json.dumps(q['knowledge_points']),
                    difficulty=q.get('difficulty', 0.5)
                )
                db.session.add(question)
                imported_count += 1
            
            db.session.commit()
            logger.info(f"成功导入 {imported_count} 道题目到数据库")
            return True, f"成功导入 {imported_count} 道题目", imported_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"导入题目失败: {e}")
            return False, f"导入题目失败: {str(e)}", 0
    
    @staticmethod
    def get_questions(page: int = 1, per_page: int = 20, difficulty: Optional[float] = None, 
                     knowledge_point: Optional[str] = None) -> Tuple[bool, str, Optional[Dict]]:
        """获取题库题目"""
        try:
            query = QuestionBank.query
            
            if difficulty is not None:
                query = query.filter(QuestionBank.difficulty == difficulty)
            
            if knowledge_point:
                query = query.filter(QuestionBank.knowledge_points.contains(knowledge_point))
            
            questions = query.paginate(page=page, per_page=per_page, error_out=False)
            
            result = {
                'questions': [q.to_dict() for q in questions.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': questions.total,
                    'pages': questions.pages,
                    'has_next': questions.has_next,
                    'has_prev': questions.has_prev
                }
            }
            
            return True, "获取成功", result
            
        except Exception as e:
            logger.error(f"获取题目失败: {e}")
            return False, f"获取题目失败: {str(e)}", None

class LearningProgressService:
    """学习进度服务"""
    
    @staticmethod
    def update_daily_progress(student_id: str, date: date, questions_answered: int, 
                            correct_answers: int, study_time_minutes: int = 0) -> Tuple[bool, str]:
        """更新每日学习进度"""
        try:
            progress_record = LearningProgress.query.filter_by(
                student_id=student_id,
                date=date
            ).first()
            
            if progress_record:
                progress_record.questions_answered += questions_answered
                progress_record.correct_answers += correct_answers
                progress_record.study_time_minutes += study_time_minutes
                progress_record.accuracy = progress_record.correct_answers / progress_record.questions_answered
            else:
                accuracy = correct_answers / questions_answered if questions_answered > 0 else 0
                progress_record = LearningProgress(
                    student_id=student_id,
                    date=date,
                    questions_answered=questions_answered,
                    correct_answers=correct_answers,
                    accuracy=accuracy,
                    study_time_minutes=study_time_minutes
                )
                db.session.add(progress_record)
            
            db.session.commit()
            return True, "学习进度更新成功"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"更新学习进度失败: {e}")
            return False, f"更新学习进度失败: {str(e)}"
    
    @staticmethod
    def get_progress_summary(student_id: str, days: int = 30) -> Tuple[bool, str, Optional[Dict]]:
        """获取学习进度摘要"""
        try:
            student = Student.query.filter_by(id=student_id).first()
            if not student:
                return False, f"学生 {student_id} 不存在", None
            
            # 获取最近N天的学习进度
            from datetime import timedelta
            start_date = date.today() - timedelta(days=days-1)
            
            progress_records = LearningProgress.query.filter(
                LearningProgress.student_id == student_id,
                LearningProgress.date >= start_date
            ).order_by(LearningProgress.date.desc()).all()
            
            # 计算统计信息
            total_questions = sum(record.questions_answered for record in progress_records)
            total_correct = sum(record.correct_answers for record in progress_records)
            total_study_time = sum(record.study_time_minutes for record in progress_records)
            avg_accuracy = total_correct / total_questions if total_questions > 0 else 0
            
            result = {
                'student_id': student_id,
                'period_days': days,
                'total_questions': total_questions,
                'total_correct': total_correct,
                'average_accuracy': avg_accuracy,
                'total_study_time_minutes': total_study_time,
                'daily_progress': [record.to_dict() for record in progress_records]
            }
            
            return True, "获取成功", result
            
        except Exception as e:
            logger.error(f"获取学习进度失败: {e}")
            return False, f"获取学习进度失败: {str(e)}", None

