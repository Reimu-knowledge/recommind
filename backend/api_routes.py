#!/usr/bin/env python3
"""
API路由定义
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, date
import logging
import traceback
import os
import sys

# 添加recommend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'recommend'))

from services import (
    StudentService, LearningSessionService, KnowledgeMasteryService,
    AnswerRecordService, QuestionBankService, LearningProgressService
)
from start import EducationRecommendationAPI

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

# 初始化推荐系统
try:
    recommendation_api = EducationRecommendationAPI()
    logger.info("推荐系统初始化成功")
except Exception as e:
    logger.error(f"推荐系统初始化失败: {e}")
    recommendation_api = None

# 错误处理装饰器
def handle_errors(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API错误: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': f'服务器内部错误: {str(e)}'
            }), 500
    wrapper.__name__ = f.__name__
    return wrapper

# 健康检查接口
@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'success',
        'message': '教育推荐系统后端服务正常运行',
        'recommendation_system': 'active' if recommendation_api else 'inactive',
        'timestamp': datetime.utcnow().isoformat()
    })

# 学生管理接口
@api_bp.route('/students', methods=['POST'])
@handle_errors
def create_student():
    """创建新学生"""
    data = request.get_json()
    
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段: id, name'
        }), 400
    
    success, message, student = StudentService.create_student(data)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 400
    
    # 初始化推荐系统中的学生
    if recommendation_api:
        initial_mastery = data.get('initial_mastery', {})
        recommendation_api.start_session(data['id'], initial_mastery)
    
    return jsonify({
        'status': 'success',
        'message': message,
        'data': student.to_dict()
    }), 201

@api_bp.route('/students/<student_id>', methods=['GET'])
@handle_errors
def get_student(student_id):
    """获取学生信息"""
    success, message, student_data = StudentService.get_student_with_stats(student_id)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': student_data
    })

@api_bp.route('/students', methods=['GET'])
@handle_errors
def get_all_students():
    """获取所有学生列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    success, message, result = StudentService.get_all_students(page, per_page)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 500
    
    return jsonify({
        'status': 'success',
        'data': result
    })

# 学习会话管理接口
@api_bp.route('/students/<student_id>/sessions', methods=['POST'])
@handle_errors
def start_learning_session(student_id):
    """开始学习会话"""
    data = request.get_json() or {}
    session_name = data.get('session_name')
    
    success, message, session = LearningSessionService.start_session(student_id, session_name)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 400
    
    # 启动推荐系统会话
    if recommendation_api:
        # 获取学生当前的知识点掌握度
        from models import KnowledgeMastery
        mastery_records = KnowledgeMastery.query.filter_by(student_id=student_id).all()
        initial_mastery = {record.knowledge_point_id: record.mastery_score for record in mastery_records}
        
        recommendation_api.start_session(student_id, initial_mastery)
    
    return jsonify({
        'status': 'success',
        'message': message,
        'data': session.to_dict()
    }), 201

@api_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@handle_errors
def end_learning_session(session_id):
    """结束学习会话"""
    success, message, session = LearningSessionService.end_session(session_id)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 400
    
    # 结束推荐系统会话
    if recommendation_api:
        recommendation_api.end_session()
    
    return jsonify({
        'status': 'success',
        'message': message,
        'data': session.to_dict()
    })

# 推荐接口
@api_bp.route('/students/<student_id>/recommendations', methods=['GET'])
@handle_errors
def get_recommendations(student_id):
    """获取学习推荐"""
    if not recommendation_api:
        return jsonify({
            'status': 'error',
            'message': '推荐系统未初始化'
        }), 500
    
    num_questions = request.args.get('num_questions', 3, type=int)
    
    # 确保学生存在
    from models import Student
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            'status': 'error',
            'message': f'学生 {student_id} 不存在'
        }), 404
    
    # 获取推荐
    result = recommendation_api.get_questions(num_questions)
    
    if result['status'] == 'error':
        return jsonify(result), 400
    
    return jsonify(result)

@api_bp.route('/students/<student_id>/answers', methods=['POST'])
@handle_errors
def submit_answers(student_id):
    """提交学生答案"""
    if not recommendation_api:
        return jsonify({
            'status': 'error',
            'message': '推荐系统未初始化'
        }), 500
    
    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少answers字段'
        }), 400
    
    answers = data['answers']
    session_id = data.get('session_id')
    
    # 确保学生存在
    from models import Student
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            'status': 'error',
            'message': f'学生 {student_id} 不存在'
        }), 404
    
    # 提交答案到推荐系统
    result = recommendation_api.submit_student_answers(answers)
    
    if result['status'] == 'error':
        return jsonify(result), 400
    
    # 保存答题记录到数据库
    success, message = AnswerRecordService.save_answer_records(student_id, session_id, result['answer_details'])
    
    if not success:
        logger.error(f"保存答题记录失败: {message}")
    
    # 更新知识点掌握度
    success, message = KnowledgeMasteryService.update_mastery(student_id, result['current_mastery'])
    
    if not success:
        logger.error(f"更新知识点掌握度失败: {message}")
    
    # 更新每日学习进度
    today = date.today()
    questions_answered = len(result['answer_details'])
    correct_answers = sum(1 for detail in result['answer_details'] if detail['correct'])
    
    LearningProgressService.update_daily_progress(student_id, today, questions_answered, correct_answers)
    
    logger.info(f"学生 {student_id} 提交答案，正确率: {correct_answers}/{questions_answered}")
    
    return jsonify(result)

# 学习分析接口
@api_bp.route('/students/<student_id>/mastery', methods=['GET'])
@handle_errors
def get_knowledge_mastery(student_id):
    """获取学生知识点掌握情况"""
    success, message, result = KnowledgeMasteryService.get_mastery_summary(student_id)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': result
    })

@api_bp.route('/students/<student_id>/weak-points', methods=['GET'])
@handle_errors
def get_weak_points(student_id):
    """获取学生薄弱知识点分析"""
    if not recommendation_api:
        return jsonify({
            'status': 'error',
            'message': '推荐系统未初始化'
        }), 500
    
    threshold = request.args.get('threshold', 0.3, type=float)
    
    result = recommendation_api.get_weak_points(threshold)
    
    if result['status'] == 'error':
        return jsonify(result), 400
    
    return jsonify(result)

@api_bp.route('/students/<student_id>/learning-history', methods=['GET'])
@handle_errors
def get_learning_history(student_id):
    """获取学生学习历史"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    success, message, result = AnswerRecordService.get_learning_history(student_id, page, per_page)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': result
    })

@api_bp.route('/students/<student_id>/progress', methods=['GET'])
@handle_errors
def get_learning_progress(student_id):
    """获取学生学习进度"""
    days = request.args.get('days', 30, type=int)
    
    success, message, result = LearningProgressService.get_progress_summary(student_id, days)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': result
    })

# 题库管理接口
@api_bp.route('/questions', methods=['GET'])
@handle_errors
def get_questions():
    """获取题库题目"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    difficulty = request.args.get('difficulty', type=float)
    knowledge_point = request.args.get('knowledge_point')
    
    success, message, result = QuestionBankService.get_questions(page, per_page, difficulty, knowledge_point)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 500
    
    return jsonify({
        'status': 'success',
        'data': result
    })

@api_bp.route('/questions/<question_id>', methods=['GET'])
@handle_errors
def get_question(question_id):
    """获取单个题目详情"""
    from models import QuestionBank
    
    question = QuestionBank.query.get(question_id)
    
    if not question:
        return jsonify({
            'status': 'error',
            'message': f'题目 {question_id} 不存在'
        }), 404
    
    return jsonify({
        'status': 'success',
        'data': question.to_dict()
    })

# 系统管理接口
@api_bp.route('/admin/import-questions', methods=['POST'])
@handle_errors
def import_questions():
    """导入题目到数据库"""
    data = request.get_json() or {}
    json_path = data.get('json_path')
    
    if not json_path:
        # 使用默认路径
        json_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'question.json')
    
    success, message, count = QuestionBankService.import_questions_from_json(json_path)
    
    if not success:
        return jsonify({
            'status': 'error',
            'message': message
        }), 400
    
    return jsonify({
        'status': 'success',
        'message': message,
        'imported_count': count
    })

@api_bp.route('/admin/stats', methods=['GET'])
@handle_errors
def get_system_stats():
    """获取系统统计信息"""
    from models import Student, LearningSession, AnswerRecord, QuestionBank
    
    stats = {
        'total_students': Student.query.filter_by(is_active=True).count(),
        'total_sessions': LearningSession.query.count(),
        'active_sessions': LearningSession.query.filter_by(is_active=True).count(),
        'total_questions_answered': AnswerRecord.query.count(),
        'total_questions_in_bank': QuestionBank.query.count(),
        'recommendation_system_status': 'active' if recommendation_api else 'inactive'
    }
    
    return jsonify({
        'status': 'success',
        'data': stats
    })

