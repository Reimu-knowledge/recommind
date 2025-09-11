#!/usr/bin/env python3
"""
配置文件
"""

import os
from datetime import timedelta

class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # 推荐系统配置
    RECOMMENDATION_CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'recommend', 'config.json')
    
    # 分页配置
    QUESTIONS_PER_PAGE = 20
    STUDENTS_PER_PAGE = 20
    ANSWER_RECORDS_PER_PAGE = 50
    
    # 学习分析配置
    MASTERY_THRESHOLD = 0.5  # 掌握度阈值
    WEAK_POINT_THRESHOLD = 0.3  # 薄弱知识点阈值
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'education_recommendation_dev.db')

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'education_recommendation.db')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'education_recommendation_test.db')
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}



