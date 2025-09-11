#!/usr/bin/env python3
"""
教育推荐系统后端API服务 - 简化版
基于Flask框架，集成学生数据库存储和推荐功能
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, date
import json
import os
import sys
import logging

# 添加recommend目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'recommend'))

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///education_recommendation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化扩展
db = SQLAlchemy(app)
CORS(app)

# 数据库模型
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

# 初始化推荐系统
try:
    # 切换到recommend目录来初始化推荐系统
    original_cwd = os.getcwd()
    recommend_dir = os.path.join(os.path.dirname(__file__), '..', 'recommend')
    os.chdir(recommend_dir)
    
    from start import EducationRecommendationAPI
    recommendation_api = EducationRecommendationAPI()
    
    # 切换回原目录
    os.chdir(original_cwd)
    
    logger.info("推荐系统初始化成功")
except Exception as e:
    logger.error(f"推荐系统初始化失败: {e}")
    recommendation_api = None

# 加载错因分析数据
error_analysis_data = {}
try:
    error_analysis_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'aligned_options_by_question.json')
    with open(error_analysis_path, 'r', encoding='utf-8') as f:
        error_analysis_data = json.load(f)
    
    # 转换为便于查询的格式
    error_analysis_dict = {}
    for item in error_analysis_data:
        question_id = item['question_id']
        error_analysis_dict[question_id] = {
            'question_text': item['question_text'],
            'options': {}
        }
        
        for option in item['options']:
            option_letter = option['option_letter']
            error_analysis_dict[question_id]['options'][option_letter] = {
                'option_text': option['option_text'],
                'knowledge_points': option['aligned_knowledge_points']
            }
    
    logger.info(f"错因分析数据加载成功，共{len(error_analysis_dict)}道题目")
except Exception as e:
    logger.error(f"错因分析数据加载失败: {e}")
    error_analysis_dict = {}

# 加载知识点映射数据
knowledge_points_mapping = {}
try:
    knowledge_points_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'formatted_nodes.csv')
    with open(knowledge_points_path, 'r', encoding='utf-8') as f:
        import csv
        reader = csv.DictReader(f)
        for row in reader:
            # 修正：name是知识点ID（如K1），id是知识点名称（如"ch14图的基本概念"）
            knowledge_points_mapping[row['name']] = row['id']
    
    logger.info(f"知识点映射数据加载成功，共{len(knowledge_points_mapping)}个知识点")
    # 打印前几个映射关系用于调试
    for i, (kp_id, kp_name) in enumerate(list(knowledge_points_mapping.items())[:5]):
        logger.info(f"  映射 {i+1}: {kp_id} -> {kp_name}")
except Exception as e:
    logger.error(f"知识点映射数据加载失败: {e}")
    knowledge_points_mapping = {}

# 加载题目数据
questions_data = {}
try:
    questions_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'question.json')
    with open(questions_path, 'r', encoding='utf-8') as f:
        questions_json = json.load(f)
        for question in questions_json['questions']:
            questions_data[question['qid']] = question
    
    logger.info(f"题目数据加载成功，共{len(questions_data)}道题目")
except Exception as e:
    logger.error(f"题目数据加载失败: {e}")
    questions_data = {}

# API路由
@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'success',
        'message': '教育推荐系统后端服务正常运行',
        'recommendation_system': 'active' if recommendation_api else 'inactive',
        'error_analysis_data': 'loaded' if error_analysis_dict else 'not_loaded',
        'error_analysis_questions': len(error_analysis_dict) if error_analysis_dict else 0,
        'knowledge_points': 'loaded' if knowledge_points_mapping else 'not_loaded',
        'knowledge_points_count': len(knowledge_points_mapping) if knowledge_points_mapping else 0,
        'questions_data': 'loaded' if questions_data else 'not_loaded',
        'questions_count': len(questions_data) if questions_data else 0,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/knowledge-graph', methods=['GET'])
def get_knowledge_graph_csv():
    """返回知识图谱CSV内容（formatted_kg.csv）"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'formatted_kg.csv')
        # 规范化路径
        csv_path = os.path.abspath(csv_path)
        if not os.path.exists(csv_path):
            logger.error(f"知识图谱CSV不存在: {csv_path}")
            return jsonify({'status': 'error', 'message': '知识图谱CSV不存在'}), 404

        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 以纯文本返回，方便前端直接解析
        from flask import Response
        return Response(content, mimetype='text/plain; charset=utf-8')
    except Exception as e:
        logger.error(f"读取知识图谱CSV失败: {e}")
        return jsonify({'status': 'error', 'message': f'读取知识图谱CSV失败: {str(e)}'}), 500

# 学生管理接口
@app.route('/api/students', methods=['POST'])
def create_student():
    """创建新学生"""
    data = request.get_json()
    
    if not data or 'id' not in data or 'name' not in data:
        return jsonify({
            'status': 'error',
            'message': '缺少必要字段: id, name'
        }), 400
    
    # 检查学生是否已存在
    existing_student = Student.query.filter_by(id=data['id']).first()
    if existing_student:
        return jsonify({
            'status': 'error',
            'message': f'学生ID {data["id"]} 已存在'
        }), 400
    
    # 创建新学生
    student = Student(
        id=data['id'],
        name=data['name'],
        email=data.get('email'),
        grade=data.get('grade')
    )
    
    db.session.add(student)
    db.session.commit()
    
    # 初始化推荐系统中的学生
    if recommendation_api:
        initial_mastery = data.get('initial_mastery', {})
        recommendation_api.start_session(data['id'], initial_mastery)
    
    logger.info(f"创建新学生: {data['id']}")
    
    return jsonify({
        'status': 'success',
        'message': f'学生 {data["id"]} 创建成功',
        'data': student.to_dict()
    }), 201

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """获取学生信息"""
    student = Student.query.filter_by(id=student_id).first()
    
    if not student:
        return jsonify({
            'status': 'error',
            'message': f'学生 {student_id} 不存在'
        }), 404
    
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
    
    return jsonify({
        'status': 'success',
        'data': student_data
    })

@app.route('/api/students', methods=['GET'])
def get_all_students():
    """获取所有学生列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
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
    
    return jsonify({
        'status': 'success',
        'data': {
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
    })

# 学习会话管理接口
@app.route('/api/students/<student_id>/sessions', methods=['POST'])
def start_learning_session(student_id):
    """开始学习会话"""
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            'status': 'error',
            'message': f'学生 {student_id} 不存在'
        }), 404
    
    data = request.get_json() or {}
    session_name = data.get('session_name', f'学习会话_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    
    # 创建学习会话
    session = LearningSession(
        student_id=student_id,
        session_name=session_name
    )
    
    db.session.add(session)
    db.session.commit()
    
    # 启动推荐系统会话
    if recommendation_api:
        # 获取学生当前的知识点掌握度
        mastery_records = KnowledgeMastery.query.filter_by(student_id=student_id).all()
        initial_mastery = {record.knowledge_point_id: record.mastery_score for record in mastery_records}
        
        recommendation_api.start_session(student_id, initial_mastery)
    
    logger.info(f"学生 {student_id} 开始学习会话: {session.id}")
    
    return jsonify({
        'status': 'success',
        'message': f'学习会话开始成功',
        'data': session.to_dict()
    }), 201

@app.route('/api/sessions/<int:session_id>', methods=['PUT'])
def end_learning_session(session_id):
    """结束学习会话"""
    session = LearningSession.query.get(session_id)
    if not session:
        return jsonify({
            'status': 'error',
            'message': f'学习会话 {session_id} 不存在'
        }), 404
    
    if not session.is_active:
        return jsonify({
            'status': 'error',
            'message': f'学习会话 {session_id} 已经结束'
        }), 400
    
    # 结束会话
    session.ended_at = datetime.utcnow()
    session.is_active = False
    
    # 计算准确率
    if session.total_questions > 0:
        session.accuracy = session.correct_answers / session.total_questions
    
    db.session.commit()
    
    # 结束推荐系统会话
    if recommendation_api:
        recommendation_api.end_session()
    
    logger.info(f"学习会话 {session_id} 结束")
    
    return jsonify({
        'status': 'success',
        'message': f'学习会话 {session_id} 结束成功',
        'data': session.to_dict()
    })

# 推荐接口
@app.route('/api/students/<student_id>/recommendations', methods=['GET'])
def get_recommendations(student_id):
    """获取学习推荐"""
    if not recommendation_api:
        return jsonify({
            'status': 'error',
            'message': '推荐系统未初始化'
        }), 500
    
    num_questions = request.args.get('num_questions', 3, type=int)
    
    # 确保学生存在
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

@app.route('/api/students/<student_id>/answers', methods=['POST'])
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
    session = None
    if session_id:
        session = LearningSession.query.get(session_id)
    
    for answer_detail in result['answer_details']:
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
    
    # 更新知识点掌握度
    for kp_id, mastery_score in result['current_mastery'].items():
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
    
    logger.info(f"学生 {student_id} 提交答案，正确率: {sum(1 for a in result['answer_details'] if a['correct']) / len(result['answer_details']):.2%}")
    
    return jsonify(result)

# 学习分析接口
@app.route('/api/students/<student_id>/mastery', methods=['GET'])
def get_knowledge_mastery(student_id):
    """获取学生知识点掌握情况"""
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            'status': 'error',
            'message': f'学生 {student_id} 不存在'
        }), 404
    
    mastery_records = KnowledgeMastery.query.filter_by(student_id=student_id).all()
    
    mastery_data = {}
    for record in mastery_records:
        mastery_data[record.knowledge_point_id] = {
            'mastery_score': record.mastery_score,
            'last_updated': record.last_updated.isoformat(),
            'practice_count': record.practice_count,
            'correct_count': record.correct_count,
            'accuracy': record.correct_count / record.practice_count if record.practice_count > 0 else 0
        }
    
    return jsonify({
        'status': 'success',
        'data': {
            'student_id': student_id,
            'knowledge_mastery': mastery_data,
            'total_knowledge_points': len(mastery_data),
            'mastered_points': len([kp for kp, data in mastery_data.items() if data['mastery_score'] >= 0.5])
        }
    })

@app.route('/api/students/<student_id>/weak-points', methods=['GET'])
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
    
    # 转换薄弱知识点格式，添加知识点名称
    weak_points_with_names = []
    for kp_id, score in result.get('weak_knowledge_points', []):
        kp_name = knowledge_points_mapping.get(kp_id, kp_id)  # 如果没有找到映射，使用原ID
        weak_points_with_names.append({
            'id': kp_id,
            'name': kp_name,
            'score': score
        })
    
    result['weak_knowledge_points'] = weak_points_with_names
    return jsonify(result)

@app.route('/api/questions/by-knowledge-point/<knowledge_point_id>', methods=['GET'])
def get_questions_by_knowledge_point(knowledge_point_id):
    """根据知识点ID获取相关题目"""
    try:
        # 查找包含该知识点的题目
        related_questions = []
        for qid, question in questions_data.items():
            if knowledge_point_id in question.get('knowledge_points', {}):
                # 转换题目格式以匹配前端需求
                formatted_question = {
                    'qid': question['qid'],
                    'content': question['content'],
                    'options': question['options'],
                    'answer': question['answer'],
                    'knowledge_points': question['knowledge_points'],
                    'difficulty': question['difficulty']
                }
                related_questions.append(formatted_question)
        
        # 获取知识点名称
        knowledge_point_name = knowledge_points_mapping.get(knowledge_point_id, knowledge_point_id)
        
        return jsonify({
            'status': 'success',
            'knowledge_point_id': knowledge_point_id,
            'knowledge_point_name': knowledge_point_name,
            'questions': related_questions,
            'total_count': len(related_questions)
        })
        
    except Exception as e:
        logger.error(f"获取知识点相关题目失败: {e}")
        return jsonify({'status': 'error', 'message': f'获取题目失败: {str(e)}'}), 500

@app.route('/api/students/<student_id>/learning-history', methods=['GET'])
def get_learning_history(student_id):
    """获取学生学习历史"""
    student = Student.query.filter_by(id=student_id).first()
    if not student:
        return jsonify({
            'status': 'error',
            'message': f'学生 {student_id} 不存在'
        }), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # 获取答题记录
    answer_records = AnswerRecord.query.filter_by(student_id=student_id).order_by(
        AnswerRecord.answered_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # 获取学习会话
    sessions = LearningSession.query.filter_by(student_id=student_id).order_by(
        LearningSession.started_at.desc()
    ).all()
    
    history_data = {
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
    
    return jsonify({
        'status': 'success',
        'data': history_data
    })

# 错因分析接口
@app.route('/api/error-analysis/<question_id>/<option_letter>', methods=['GET'])
def get_error_analysis(question_id, option_letter):
    """获取题目选项的错因分析"""
    try:
        # 验证参数
        if not question_id or not option_letter:
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数: question_id, option_letter'
            }), 400
        
        # 转换为大写
        option_letter = option_letter.upper()
        
        # 检查题目是否存在
        if question_id not in error_analysis_dict:
            return jsonify({
                'status': 'error',
                'message': f'题目 {question_id} 不存在'
            }), 404
        
        question_data = error_analysis_dict[question_id]
        
        # 检查选项是否存在
        if option_letter not in question_data['options']:
            return jsonify({
                'status': 'error',
                'message': f'题目 {question_id} 的选项 {option_letter} 不存在'
            }), 404
        
        option_data = question_data['options'][option_letter]
        
        # 构建错因分析结果 - 简化版，只返回需要巩固的知识点
        knowledge_points_to_review = []
        
        for kp in option_data['knowledge_points']:
            # 只返回高相关和中等相关的知识点
            if kp['similarity'] >= 0.5:
                knowledge_points_to_review.append({
                    'knowledge_point': kp['aligned_kg_node'],
                    'similarity': kp['similarity'],
                    'priority': 'high' if kp['similarity'] >= 0.8 else 'medium'
                })
        
        # 按相似度排序，优先显示高相关知识点
        knowledge_points_to_review.sort(key=lambda x: x['similarity'], reverse=True)
        
        error_analysis = {
            'question_id': question_id,
            'selected_option': option_letter,
            'knowledge_points_to_review': knowledge_points_to_review
        }
        
        logger.info(f"获取错因分析: {question_id}-{option_letter}")
        
        return jsonify({
            'status': 'success',
            'data': error_analysis
        })
        
    except Exception as e:
        logger.error(f"获取错因分析失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取错因分析失败: {str(e)}'
        }), 500

@app.route('/api/error-analysis/<question_id>', methods=['GET'])
def get_question_error_analysis(question_id):
    """获取题目的完整错因分析（所有选项）"""
    try:
        # 检查题目是否存在
        if question_id not in error_analysis_dict:
            return jsonify({
                'status': 'error',
                'message': f'题目 {question_id} 不存在'
            }), 404
        
        question_data = error_analysis_dict[question_id]
        
        # 构建完整错因分析 - 简化版
        complete_analysis = {
            'question_id': question_id,
            'question_text': question_data['question_text'],
            'options_analysis': {}
        }
        
        for option_letter, option_data in question_data['options'].items():
            # 只统计需要巩固的知识点
            knowledge_points_to_review = []
            for kp in option_data['knowledge_points']:
                if kp['similarity'] >= 0.5:
                    knowledge_points_to_review.append({
                        'knowledge_point': kp['aligned_kg_node'],
                        'similarity': kp['similarity']
                    })
            
            complete_analysis['options_analysis'][option_letter] = {
                'option_text': option_data['option_text'],
                'knowledge_points_to_review': knowledge_points_to_review,
                'review_count': len(knowledge_points_to_review)
            }
        
        logger.info(f"获取完整错因分析: {question_id}")
        
        return jsonify({
            'status': 'success',
            'data': complete_analysis
        })
        
    except Exception as e:
        logger.error(f"获取完整错因分析失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取完整错因分析失败: {str(e)}'
        }), 500

# 教师端API接口
@app.route('/api/teacher/students', methods=['GET'])
def get_teacher_all_students():
    """教师端：获取所有学生列表"""
    try:
        students = Student.query.filter_by(is_active=True).all()
        
        student_list = []
        for student in students:
            # 获取学习统计
            total_questions = AnswerRecord.query.filter_by(student_id=student.id).count()
            correct_answers = AnswerRecord.query.filter_by(student_id=student.id, is_correct=True).count()
            total_sessions = LearningSession.query.filter_by(student_id=student.id).count()
            
            # 获取知识点掌握情况
            mastery_records = KnowledgeMastery.query.filter_by(student_id=student.id).all()
            knowledge_scores = []
            for record in mastery_records:
                kp_name = knowledge_points_mapping.get(record.knowledge_point_id, record.knowledge_point_id)
                knowledge_scores.append({
                    'knowledge_point_id': record.knowledge_point_id,
                    'knowledge_point_name': kp_name,
                    'score': int(record.mastery_score * 100),  # 转换为百分比
                    'practice_count': record.practice_count,
                    'correct_count': record.correct_count
                })
            
            # 按知识点ID排序
            knowledge_scores.sort(key=lambda x: x['knowledge_point_id'])
            
            student_data = {
                'id': student.id,
                'name': student.name,
                'email': student.email,
                'grade': student.grade,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'correct_rate': int((correct_answers / total_questions * 100) if total_questions > 0 else 0),
                'total_sessions': total_sessions,
                'knowledge_scores': knowledge_scores,
                'last_active': student.updated_at.isoformat() if student.updated_at else student.created_at.isoformat(),
                'created_at': student.created_at.isoformat()
            }
            student_list.append(student_data)
        
        return jsonify({
            'status': 'success',
            'students': student_list,
            'total_count': len(student_list)
        })
        
    except Exception as e:
        logger.error(f"获取学生列表失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取学生列表失败: {str(e)}'
        }), 500

@app.route('/api/teacher/students/<student_id>', methods=['GET'])
def get_teacher_student_detail(student_id):
    """教师端：获取学生详细信息"""
    try:
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return jsonify({
                'status': 'error',
                'message': f'学生 {student_id} 不存在'
            }), 404
        
        # 获取学习统计
        total_questions = AnswerRecord.query.filter_by(student_id=student_id).count()
        correct_answers = AnswerRecord.query.filter_by(student_id=student_id, is_correct=True).count()
        total_sessions = LearningSession.query.filter_by(student_id=student_id).count()
        
        # 获取知识点掌握详情
        mastery_records = KnowledgeMastery.query.filter_by(student_id=student_id).all()
        knowledge_scores = []
        for record in mastery_records:
            kp_name = knowledge_points_mapping.get(record.knowledge_point_id, record.knowledge_point_id)
            knowledge_scores.append({
                'knowledge_point_id': record.knowledge_point_id,
                'knowledge_point_name': kp_name,
                'score': int(record.mastery_score * 100),
                'practice_count': record.practice_count,
                'correct_count': record.correct_count,
                'accuracy': int((record.correct_count / record.practice_count * 100) if record.practice_count > 0 else 0),
                'last_updated': record.last_updated.isoformat()
            })
        
        # 按知识点ID排序
        knowledge_scores.sort(key=lambda x: x['knowledge_point_id'])
        
        # 获取最近的学习会话
        recent_sessions = LearningSession.query.filter_by(student_id=student_id).order_by(
            LearningSession.started_at.desc()
        ).limit(5).all()
        
        student_detail = {
            'id': student.id,
            'name': student.name,
            'email': student.email,
            'grade': student.grade,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'correct_rate': int((correct_answers / total_questions * 100) if total_questions > 0 else 0),
            'total_sessions': total_sessions,
            'knowledge_scores': knowledge_scores,
            'recent_sessions': [session.to_dict() for session in recent_sessions],
            'last_active': student.updated_at.isoformat() if student.updated_at else student.created_at.isoformat(),
            'created_at': student.created_at.isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': student_detail
        })
        
    except Exception as e:
        logger.error(f"获取学生详情失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取学生详情失败: {str(e)}'
        }), 500

@app.route('/api/teacher/stats', methods=['GET'])
def get_teacher_overall_stats():
    """教师端：获取总体统计数据"""
    try:
        # 学生统计
        total_students = Student.query.filter_by(is_active=True).count()
        
        # 学习统计
        total_questions = AnswerRecord.query.count()
        correct_answers = AnswerRecord.query.filter_by(is_correct=True).count()
        average_score = int((correct_answers / total_questions * 100) if total_questions > 0 else 0)
        
        # 活跃学生（最近7天有学习记录）
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_students = db.session.query(AnswerRecord.student_id).filter(
            AnswerRecord.answered_at >= seven_days_ago
        ).distinct().count()
        
        # 知识点统计
        total_knowledge_points = len(knowledge_points_mapping)
        
        # 学习会话统计
        total_sessions = LearningSession.query.count()
        active_sessions = LearningSession.query.filter_by(is_active=True).count()
        
        stats = {
            'total_students': total_students,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'average_score': average_score,
            'active_students': active_students,
            'total_knowledge_points': total_knowledge_points,
            'total_sessions': total_sessions,
            'active_sessions': active_sessions
        }
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取统计数据失败: {str(e)}'
        }), 500

@app.route('/api/teacher/knowledge-points', methods=['GET'])
def get_teacher_knowledge_points():
    """教师端：获取知识点列表"""
    try:
        knowledge_points = []
        for kp_id, kp_name in knowledge_points_mapping.items():
            knowledge_points.append({
                'id': kp_id,
                'name': kp_name
            })
        
        # 按ID排序
        knowledge_points.sort(key=lambda x: x['id'])
        
        return jsonify({
            'status': 'success',
            'knowledge_points': knowledge_points,
            'total_count': len(knowledge_points)
        })
        
    except Exception as e:
        logger.error(f"获取知识点列表失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取知识点列表失败: {str(e)}'
        }), 500

@app.route('/api/teacher/students/mastery', methods=['GET'])
def get_teacher_all_students_mastery():
    """教师端：获取所有学生的知识点掌握情况"""
    try:
        students = Student.query.filter_by(is_active=True).all()
        
        students_mastery = []
        for student in students:
            # 获取知识点掌握情况
            mastery_records = KnowledgeMastery.query.filter_by(student_id=student.id).all()
            
            knowledge_scores = []
            for record in mastery_records:
                kp_name = knowledge_points_mapping.get(record.knowledge_point_id, record.knowledge_point_id)
                knowledge_scores.append({
                    'knowledge_point_id': record.knowledge_point_id,
                    'knowledge_point_name': kp_name,
                    'score': int(record.mastery_score * 100),
                    'practice_count': record.practice_count,
                    'correct_count': record.correct_count
                })
            
            # 按知识点ID排序
            knowledge_scores.sort(key=lambda x: x['knowledge_point_id'])
            
            student_mastery = {
                'student_id': student.id,
                'student_name': student.name,
                'knowledge_scores': knowledge_scores,
                'total_knowledge_points': len(knowledge_scores),
                'mastered_points': len([kp for kp in knowledge_scores if kp['score'] >= 70]),
                'weak_points': len([kp for kp in knowledge_scores if kp['score'] < 70])
            }
            students_mastery.append(student_mastery)
        
        return jsonify({
            'status': 'success',
            'students': students_mastery,
            'total_count': len(students_mastery)
        })
        
    except Exception as e:
        logger.error(f"获取学生掌握情况失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取学生掌握情况失败: {str(e)}'
        }), 500

@app.route('/api/teacher/knowledge-points/stats', methods=['GET'])
def get_teacher_knowledge_point_stats():
    """教师端：获取知识点总体掌握情况"""
    try:
        knowledge_point_stats = []
        
        for kp_id, kp_name in knowledge_points_mapping.items():
            # 获取该知识点的所有掌握记录
            mastery_records = KnowledgeMastery.query.filter_by(knowledge_point_id=kp_id).all()
            
            if not mastery_records:
                continue
            
            # 计算统计信息
            total_students = len(mastery_records)
            scores = [record.mastery_score * 100 for record in mastery_records]  # 转换为百分比
            average_score = int(sum(scores) / len(scores)) if scores else 0
            mastered_students = len([score for score in scores if score >= 70])
            weak_students = len([score for score in scores if score < 70])
            
            # 计算练习统计
            total_practice = sum(record.practice_count for record in mastery_records)
            total_correct = sum(record.correct_count for record in mastery_records)
            overall_accuracy = int((total_correct / total_practice * 100) if total_practice > 0 else 0)
            
            kp_stat = {
                'knowledge_point_id': kp_id,
                'knowledge_point_name': kp_name,
                'total_students': total_students,
                'average_score': average_score,
                'mastered_students': mastered_students,
                'weak_students': weak_students,
                'mastery_rate': int((mastered_students / total_students * 100) if total_students > 0 else 0),
                'total_practice': total_practice,
                'total_correct': total_correct,
                'overall_accuracy': overall_accuracy
            }
            knowledge_point_stats.append(kp_stat)
        
        # 按平均分排序
        knowledge_point_stats.sort(key=lambda x: x['average_score'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'knowledge_point_stats': knowledge_point_stats,
            'total_count': len(knowledge_point_stats)
        })
        
    except Exception as e:
        logger.error(f"获取知识点统计失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取知识点统计失败: {str(e)}'
        }), 500

@app.route('/api/teacher/students/<student_id>/recommendation', methods=['POST'])
def update_student_recommendation(student_id):
    """教师端：更新学生推荐方向"""
    try:
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return jsonify({
                'status': 'error',
                'message': f'学生 {student_id} 不存在'
            }), 404
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': '缺少请求数据'
            }), 400
        
        knowledge_points = data.get('knowledge_points', [])
        priority = data.get('priority', 'medium')
        
        if not knowledge_points:
            return jsonify({
                'status': 'error',
                'message': '请选择至少一个知识点'
            }), 400
        
        # 这里可以实现推荐方向的更新逻辑
        # 例如：更新学生的推荐权重、设置特殊标记等
        
        logger.info(f"更新学生 {student_id} 推荐方向: {knowledge_points}, 优先级: {priority}")
        
        return jsonify({
            'status': 'success',
            'message': f'已为学生 {student.name} 更新推荐方向',
            'data': {
                'student_id': student_id,
                'knowledge_points': knowledge_points,
                'priority': priority,
                'updated_at': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"更新学生推荐方向失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'更新学生推荐方向失败: {str(e)}'
        }), 500

@app.route('/api/teacher/students/<student_id>/answers', methods=['GET'])
def get_teacher_student_answers(student_id):
    """教师端：获取学生答题记录"""
    try:
        student = Student.query.filter_by(id=student_id).first()
        if not student:
            return jsonify({
                'status': 'error',
                'message': f'学生 {student_id} 不存在'
            }), 404
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # 获取答题记录
        answer_records = AnswerRecord.query.filter_by(student_id=student_id).order_by(
            AnswerRecord.answered_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        answers = []
        for record in answer_records.items:
            answer_data = record.to_dict()
            # 添加题目信息
            if record.question_id in questions_data:
                question_info = questions_data[record.question_id]
                answer_data['question_content'] = question_info.get('content', '')
                answer_data['question_options'] = question_info.get('options', {})
            
            answers.append(answer_data)
        
        return jsonify({
            'status': 'success',
            'answers': answers,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': answer_records.total,
                'pages': answer_records.pages,
                'has_next': answer_records.has_next,
                'has_prev': answer_records.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"获取学生答题记录失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'获取学生答题记录失败: {str(e)}'
        }), 500

@app.route('/api/teacher/export/students', methods=['GET'])
def export_student_data():
    """教师端：导出学生数据"""
    try:
        format_type = request.args.get('format', 'csv')
        
        if format_type == 'csv':
            import csv
            import io
            
            # 获取所有学生数据
            students = Student.query.filter_by(is_active=True).all()
            
            # 创建CSV内容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 写入表头
            writer.writerow([
                '学号', '姓名', '邮箱', '年级', '完成题目数', '正确题目数', 
                '正确率', '学习会话数', '创建时间', '最后活跃时间'
            ])
            
            # 写入学生数据
            for student in students:
                total_questions = AnswerRecord.query.filter_by(student_id=student.id).count()
                correct_answers = AnswerRecord.query.filter_by(student_id=student.id, is_correct=True).count()
                total_sessions = LearningSession.query.filter_by(student_id=student.id).count()
                correct_rate = int((correct_answers / total_questions * 100) if total_questions > 0 else 0)
                
                writer.writerow([
                    student.id,
                    student.name,
                    student.email or '',
                    student.grade or '',
                    total_questions,
                    correct_answers,
                    f'{correct_rate}%',
                    total_sessions,
                    student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    student.updated_at.strftime('%Y-%m-%d %H:%M:%S') if student.updated_at else ''
                ])
            
            # 返回CSV文件
            from flask import Response
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=students_data.csv'}
            )
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'不支持的导出格式: {format_type}'
            }), 400
        
    except Exception as e:
        logger.error(f"导出学生数据失败: {e}")
        return jsonify({
            'status': 'error',
            'message': f'导出学生数据失败: {str(e)}'
        }), 500

# 初始化数据库
def init_database():
    """初始化数据库"""
    with app.app_context():
        db.create_all()
        logger.info("数据库初始化完成")

if __name__ == '__main__':
    # 初始化数据库
    init_database()
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5000)
