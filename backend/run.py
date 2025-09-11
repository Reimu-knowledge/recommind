#!/usr/bin/env python3
"""
后端服务启动文件
"""

import os
import sys
from flask import Flask
from flask_cors import CORS
from config import config
from models import db
from api_routes import api_bp
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(config_name='default'):
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    
    # 初始化数据库
    with app.app_context():
        db.create_all()
        
        # 如果题库为空，从JSON文件导入题目
        from models import QuestionBank
        if QuestionBank.query.count() == 0:
            import_questions_from_json()
        
        logger.info("数据库初始化完成")
    
    return app

def import_questions_from_json():
    """从JSON文件导入题目到数据库"""
    try:
        import json
        from models import QuestionBank
        
        json_path = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'question.json')
        
        if not os.path.exists(json_path):
            logger.warning(f"题目文件不存在: {json_path}")
            return
        
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
        
    except Exception as e:
        logger.error(f"导入题目失败: {e}")
        db.session.rollback()

if __name__ == '__main__':
    # 获取配置环境
    config_name = os.environ.get('FLASK_ENV', 'default')
    
    # 创建应用
    app = create_app(config_name)
    
    # 启动应用
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"启动教育推荐系统后端服务...")
    logger.info(f"环境: {config_name}")
    logger.info(f"地址: http://{host}:{port}")
    logger.info(f"调试模式: {debug}")
    
    app.run(debug=debug, host=host, port=port)



