#!/usr/bin/env python3
"""
CSrecomMIND 后端API服务
提供智能教育推荐系统的RESTful API接口
"""

import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import db
from recommendation_engine import recommendation_engine

app = Flask(__name__)
CORS(app)

# 题目数据库
QUESTIONS_DATABASE = [
    {
        "questionId": "Q1",
        "description": "集合A={1,2,3}，集合B={2,3,4}，求A∪B",
        "knowledgePoint": "K1",
        "knowledgePointName": "集合运算",
        "options": [
            {"id": "A", "text": "{1,2,3}"},
            {"id": "B", "text": "{2,3}"},
            {"id": "C", "text": "{1,2,3,4}"},
            {"id": "D", "text": "{4}"}
        ],
        "correctAnswer": "C",
        "difficulty": 0.5,
        "score": 0.8
    },
    {
        "questionId": "Q2", 
        "description": "下列哪个是自反关系？",
        "knowledgePoint": "K2",
        "knowledgePointName": "关系映射",
        "options": [
            {"id": "A", "text": "R={(1,1),(2,2)}"},
            {"id": "B", "text": "R={(1,2),(2,1)}"},
            {"id": "C", "text": "R={(1,1),(1,2)}"},
            {"id": "D", "text": "R={(2,1)}"}
        ],
        "correctAnswer": "A",
        "difficulty": 0.6,
        "score": 0.7
    },
    {
        "questionId": "Q3",
        "description": "在有向图中，顶点的入度定义为？",
        "knowledgePoint": "K3", 
        "knowledgePointName": "图基本概念",
        "options": [
            {"id": "A", "text": "指向该顶点的边数"},
            {"id": "B", "text": "从该顶点出发的边数"},
            {"id": "C", "text": "与该顶点相连的边数"},
            {"id": "D", "text": "该顶点的标号"}
        ],
        "correctAnswer": "A",
        "difficulty": 0.4,
        "score": 0.9
    },
    {
        "questionId": "Q4",
        "description": "无向图G有6个顶点，每个顶点的度数都是3，那么图G有多少条边？",
        "knowledgePoint": "K8",
        "knowledgePointName": "度的概念",
        "options": [
            {"id": "A", "text": "6条"},
            {"id": "B", "text": "9条"},
            {"id": "C", "text": "12条"},
            {"id": "D", "text": "18条"}
        ],
        "correctAnswer": "B",
        "difficulty": 0.7,
        "score": 0.6
    },
    {
        "questionId": "Q5",
        "description": "完全图K5有多少条边？",
        "knowledgePoint": "K3",
        "knowledgePointName": "图基本概念",
        "options": [
            {"id": "A", "text": "5条"},
            {"id": "B", "text": "10条"},
            {"id": "C", "text": "15条"},
            {"id": "D", "text": "20条"}
        ],
        "correctAnswer": "B",
        "difficulty": 0.6,
        "score": 0.7
    }
]

# 知识点信息
KNOWLEDGE_POINTS = {
    "K1": {"name": "集合运算", "description": "集合的并、交、差运算"},
    "K2": {"name": "关系映射", "description": "关系的性质和映射概念"},
    "K3": {"name": "图基本概念", "description": "图的基本定义和性质"},
    "K8": {"name": "度的概念", "description": "顶点的度数和握手定理"}
}

# 学生学习状态存储（临时，主要用于兼容）
student_sessions = {}

# 加载错因分析数据
def load_error_analysis_data():
    """加载错因分析数据"""
    try:
        # 获取错因分析文件路径
        current_dir = os.path.dirname(__file__)
        error_analysis_file = os.path.join(current_dir, '..', 'error_analysis', 'question_knowledge_mapping_v2.json')
        
        if os.path.exists(error_analysis_file):
            with open(error_analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"⚠️ 错因分析文件不存在: {error_analysis_file}")
            return {}
    except Exception as e:
        print(f"❌ 加载错因分析数据失败: {e}")
        return {}

# 加载错因分析数据
error_analysis_data = load_error_analysis_data()
print(f"📊 已加载 {len(error_analysis_data)} 道题目的错因分析数据")

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "success",
        "message": "CSrecomMIND API服务正常运行",
        "version": "1.0.0",
        "features": ["智能推荐", "答题判分", "学习分析", "薄弱知识点诊断"]
    })

@app.route('/api/student/recommend-questions', methods=['POST'])
def get_recommend_questions():
    """获取推荐题目"""
    try:
        data = request.get_json()
        student_id = data.get('studentId')
        knowledge_points = data.get('knowledgePoints', [])
        
        print(f"📝 推荐请求: 学生={student_id}, 知识点={knowledge_points}")
        
        if not student_id:
            return jsonify({
                "code": 400,
                "message": "缺少studentId参数",
                "data": None
            }), 400
        
        # 使用智能推荐引擎
        recommended_questions, reason = recommendation_engine.recommend_questions(
            student_id, knowledge_points, num_questions=3
        )
        
        # 获取学生统计信息
        stats = db.get_student_statistics(student_id)
        batch_number = stats.get('totalQuestions', 0) // 3 + 1
        
        print(f"✅ 推荐了 {len(recommended_questions)} 道题目")
        print(f"📊 推荐原因: {reason}")
        
        return jsonify({
            "code": 200,
            "message": "推荐题目获取成功",
            "data": {
                "questions": recommended_questions,
                "batchNumber": batch_number,
                "totalQuestions": len(recommended_questions),
                "recommendationReason": reason,
                "studentStats": {
                    "totalQuestions": stats.get('totalQuestions', 0),
                    "accuracy": stats.get('accuracy', 0),
                    "averageMastery": stats.get('averageMastery', 0)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ 获取推荐题目时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/submit-answer', methods=['POST'])
def submit_answer():
    """提交答案"""
    try:
        data = request.get_json()
        question_id = data.get('questionId')
        student_id = data.get('studentId')
        selected_option = data.get('selectedOption')
        response_time = data.get('responseTimeSeconds', 0)
        
        print(f"📤 答案提交: 题目={question_id}, 学生={student_id}, 答案={selected_option}")
        
        if not all([question_id, student_id, selected_option]):
            return jsonify({
                "code": 400,
                "message": "缺少必要参数",
                "data": None
            }), 400
        
        # 查找题目
        question = next((q for q in QUESTIONS_DATABASE if q['questionId'] == question_id), None)
        if not question:
            return jsonify({
                "code": 404,
                "message": "题目不存在",
                "data": None
            }), 404
        
        # 判分
        is_correct = question['correctAnswer'] == selected_option
        
        # 确保学生存在
        db.create_student(student_id, student_id, f"{student_id}@example.com")
        
        # 记录答题历史到数据库
        db.record_answer(
            student_id, question_id, selected_option, is_correct,
            question['knowledgePoint'], question.get('difficulty', 0.5),
            response_time, 1
        )
        
        # 更新知识点掌握度
        db.update_mastery(
            student_id, question['knowledgePoint'], is_correct,
            question.get('difficulty', 0.5)
        )
        
        # 更新推荐结果
        db.update_recommendation_result(student_id, question_id, is_correct)
        
        # 获取更新后的掌握度
        current_mastery = db.get_student_mastery(student_id)
        
        # 获取学生统计
        stats = db.get_student_statistics(student_id)
        
        print(f"🎯 判分结果: {'正确' if is_correct else '错误'}")
        print(f"📊 更新后掌握度: {current_mastery}")
        
        return jsonify({
            "code": 200,
            "message": "答案提交成功",
            "data": {
                "isCorrect": is_correct,
                "correctAnswer": question['correctAnswer'],
                "selectedAnswer": selected_option,
                "currentMastery": current_mastery,
                "knowledgePoint": question['knowledgePoint'],
                "knowledgePointName": question['knowledgePointName'],
                "studentStats": {
                    "totalQuestions": stats.get('totalQuestions', 0),
                    "accuracy": stats.get('accuracy', 0),
                    "averageMastery": stats.get('averageMastery', 0)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ 提交答案时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/get-explanation', methods=['POST'])
def get_explanation():
    """获取题目解析"""
    try:
        data = request.get_json()
        question_id = data.get('questionId')
        student_id = data.get('studentId')
        selected_option = data.get('selectedOption')
        
        print(f"📖 解析请求: 题目={question_id}, 答案={selected_option}")
        
        # 题目解析库
        explanations = {
            "Q1": "集合的并集A∪B包含所有属于A或B的元素。A={1,2,3}，B={2,3,4}，所以A∪B = {1,2,3,4}。",
            "Q2": "自反关系要求每个元素都与自己相关。R={(1,1),(2,2)}中，元素1和2都与自己相关，满足自反性。",
            "Q3": "在有向图中，顶点的入度是指向该顶点的边的数量，出度是从该顶点出发的边的数量。",
            "Q4": "根据握手定理，所有顶点度数之和等于边数的两倍。6个顶点，每个度数为3，总度数为18，所以边数为9。",
            "Q5": "完全图Kn有n(n-1)/2条边。K5有5个顶点，所以边数为5×4/2=10条。"
        }
        
        explanation = explanations.get(question_id, "这是一道关于图论基础知识的题目，需要理解相关概念和定理。")
        
        return jsonify({
            "code": 200,
            "message": "解析获取成功",
            "data": {
                "explanation": f"{explanation} 您选择的答案是{selected_option}。"
            }
        })
        
    except Exception as e:
        print(f"❌ 获取解析时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/weak-knowledge-points', methods=['GET'])
def get_weak_knowledge_points():
    """获取薄弱知识点"""
    try:
        student_id = request.args.get('studentId')
        
        print(f"📊 薄弱知识点请求: 学生={student_id}")
        
        if not student_id:
            return jsonify({
                "code": 400,
                "message": "缺少studentId参数",
                "data": None
            }), 400
        
        # 确保学生存在
        db.create_student(student_id, student_id, f"{student_id}@example.com")
        
        # 从数据库获取薄弱知识点
        weak_points = db.get_weak_knowledge_points(student_id, threshold=0.5)
        
        # 获取学生统计
        stats = db.get_student_statistics(student_id)
        mastery = db.get_student_mastery(student_id)
        
        # 计算掌握情况
        mastered_count = len([kp for kp in mastery.values() if kp >= 0.5])
        total_count = len(mastery)
        
        print(f"📈 发现 {len(weak_points)} 个薄弱知识点")
        
        return jsonify({
            "code": 200,
            "message": "薄弱知识点获取成功",
            "data": {
                "weakKnowledgePoints": weak_points,
                "progressSummary": {
                    "mastered": mastered_count,
                    "weak": len(weak_points),
                    "total": total_count,
                    "averageMastery": stats.get('averageMastery', 0),
                    "totalQuestions": stats.get('totalQuestions', 0),
                    "accuracy": stats.get('accuracy', 0)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ 获取薄弱知识点时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/progress', methods=['GET'])
def get_student_progress():
    """获取学生学习进展"""
    try:
        student_id = request.args.get('studentId')
        
        if not student_id:
            return jsonify({
                "code": 400,
                "message": "缺少studentId参数",
                "data": None
            }), 400
        
        # 确保学生存在
        db.create_student(student_id, student_id, f"{student_id}@example.com")
        
        # 获取学生数据
        mastery = db.get_student_mastery(student_id)
        stats = db.get_student_statistics(student_id)
        weak_points = db.get_weak_knowledge_points(student_id)
        learning_trend = db.get_learning_trend(student_id, 7)
        
        # 分析学习模式
        learning_pattern = recommendation_engine.analyze_learning_pattern(student_id)
        
        return jsonify({
            "code": 200,
            "message": "学习进展获取成功",
            "data": {
                "studentId": student_id,
                "mastery": mastery,
                "statistics": stats,
                "weakKnowledgePoints": weak_points,
                "learningTrend": learning_trend,
                "learningPattern": learning_pattern,
                "progressSummary": {
                    "totalQuestions": stats.get('totalQuestions', 0),
                    "accuracy": stats.get('accuracy', 0),
                    "averageMastery": stats.get('averageMastery', 0),
                    "weakPointsCount": len(weak_points),
                    "studyDays": len(learning_trend)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ 获取学习进展时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/error-analysis', methods=['POST'])
def get_error_analysis():
    """获取错因分析"""
    try:
        data = request.get_json()
        question_id = data.get('questionId')
        student_id = data.get('studentId')
        selected_option = data.get('selectedOption')
        
        print(f"🔍 错因分析请求: 题目={question_id}, 学生={student_id}, 选择={selected_option}")
        
        if not all([question_id, student_id, selected_option]):
            return jsonify({
                "code": 400,
                "message": "缺少必要参数",
                "data": None
            }), 400
        
        # 查找题目
        question = next((q for q in QUESTIONS_DATABASE if q['questionId'] == question_id), None)
        if not question:
            return jsonify({
                "code": 404,
                "message": "题目不存在",
                "data": None
            }), 404
        
        # 检查是否答错
        is_correct = question['correctAnswer'] == selected_option
        if is_correct:
            return jsonify({
                "code": 200,
                "message": "答案正确，无需错因分析",
                "data": {
                    "isCorrect": True,
                    "analysis": "恭喜您答对了！这道题您掌握得很好。"
                }
            })
        
        # 获取错因分析数据
        question_key = question_id.replace('Q', '')  # Q1 -> 1
        error_data = error_analysis_data.get(question_key)
        
        if not error_data:
            # 如果没有错因分析数据，提供通用分析
            return jsonify({
                "code": 200,
                "message": "错因分析获取成功",
                "data": {
                    "isCorrect": False,
                    "selectedOption": selected_option,
                    "correctAnswer": question['correctAnswer'],
                    "analysis": f"您选择了{selected_option}，正确答案是{question['correctAnswer']}。这道题考查的是{question['knowledgePointName']}相关知识，建议您加强相关概念的理解。",
                    "knowledgePoints": [question['knowledgePoint']],
                    "suggestions": [
                        f"复习{question['knowledgePointName']}的基本概念",
                        "多做相关练习题",
                        "理解题目的核心考查点"
                    ]
                }
            })
        
        # 分析错误选项对应的知识点
        option_key = f"option_{selected_option.lower()}"
        error_concepts = error_data.get(f"{option_key}_concepts", [])
        
        # 获取题目相关概念
        question_concepts = error_data.get("question_concepts", [])
        
        # 生成错因分析
        analysis_parts = []
        
        if error_concepts:
            analysis_parts.append(f"您选择了{selected_option}，这个选项涉及的知识点包括：{', '.join(error_concepts[:3])}")
            analysis_parts.append("这些概念可能导致了您的错误理解。")
        else:
            analysis_parts.append(f"您选择了{selected_option}，正确答案是{question['correctAnswer']}。")
        
        if question_concepts:
            analysis_parts.append(f"这道题主要考查：{', '.join(question_concepts[:3])}")
        
        analysis_parts.append("建议您重点复习相关概念，加深理解。")
        
        analysis = " ".join(analysis_parts)
        
        # 生成学习建议
        suggestions = [
            f"重点复习{question['knowledgePointName']}相关概念",
            "理解题目考查的核心知识点",
            "多做类似题目的练习"
        ]
        
        if error_concepts:
            suggestions.insert(0, f"重点理解：{', '.join(error_concepts[:2])}")
        
        print(f"✅ 错因分析完成: {len(error_concepts)}个错误知识点")
        
        return jsonify({
            "code": 200,
            "message": "错因分析获取成功",
            "data": {
                "isCorrect": False,
                "selectedOption": selected_option,
                "correctAnswer": question['correctAnswer'],
                "analysis": analysis,
                "knowledgePoints": list(set(error_concepts + [question['knowledgePoint']])),
                "errorConcepts": error_concepts,
                "questionConcepts": question_concepts,
                "suggestions": suggestions
            }
        })
        
    except Exception as e:
        print(f"❌ 获取错因分析时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/learning-analysis', methods=['GET'])
def get_learning_analysis():
    """获取学习分析报告"""
    try:
        student_id = request.args.get('studentId')
        
        if not student_id:
            return jsonify({
                "code": 400,
                "message": "缺少studentId参数",
                "data": None
            }), 400
        
        # 确保学生存在
        db.create_student(student_id, student_id, f"{student_id}@example.com")
        
        # 获取学习分析数据
        stats = db.get_student_statistics(student_id)
        mastery = db.get_student_mastery(student_id)
        weak_points = db.get_weak_knowledge_points(student_id)
        learning_trend = db.get_learning_trend(student_id, 30)  # 30天趋势
        recommendation_history = db.get_recommendation_history(student_id, 50)
        
        # 分析学习模式
        learning_pattern = recommendation_engine.analyze_learning_pattern(student_id)
        
        # 计算学习建议
        suggestions = []
        if stats.get('accuracy', 0) < 60:
            suggestions.append("建议放慢学习节奏，重点理解基础概念")
        if len(weak_points) > 2:
            suggestions.append("建议制定专项练习计划，重点攻克薄弱知识点")
        if stats.get('recentAccuracy', 0) > 85:
            suggestions.append("学习效果良好，可以尝试更有挑战性的题目")
        
        suggestions.extend(learning_pattern.get('recommendations', []))
        
        return jsonify({
            "code": 200,
            "message": "学习分析获取成功",
            "data": {
                "studentId": student_id,
                "overview": {
                    "totalQuestions": stats.get('totalQuestions', 0),
                    "accuracy": stats.get('accuracy', 0),
                    "averageMastery": stats.get('averageMastery', 0),
                    "studyTimeMinutes": stats.get('studyTimeMinutes', 0),
                    "weakPointsCount": len(weak_points)
                },
                "mastery": mastery,
                "weakKnowledgePoints": weak_points,
                "learningTrend": learning_trend,
                "learningPattern": learning_pattern,
                "recommendationHistory": recommendation_history,
                "suggestions": suggestions,
                "performanceMetrics": {
                    "recentAccuracy": stats.get('recentAccuracy', 0),
                    "totalPractice": stats.get('totalPractice', 0),
                    "studyDays": len(learning_trend),
                    "averageQuestionsPerDay": round(stats.get('totalQuestions', 0) / max(len(learning_trend), 1), 1)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ 获取学习分析时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

@app.route('/api/student/recommendation-history', methods=['GET'])
def get_recommendation_history():
    """获取推荐历史"""
    try:
        student_id = request.args.get('studentId')
        limit = int(request.args.get('limit', 20))
        
        if not student_id:
            return jsonify({
                "code": 400,
                "message": "缺少studentId参数",
                "data": None
            }), 400
        
        # 确保学生存在
        db.create_student(student_id, student_id, f"{student_id}@example.com")
        
        # 获取推荐历史
        history = db.get_recommendation_history(student_id, limit)
        
        return jsonify({
            "code": 200,
            "message": "推荐历史获取成功",
            "data": {
                "studentId": student_id,
                "recommendationHistory": history,
                "summary": {
                    "totalRecommendations": len(history),
                    "answeredRecommendations": len([h for h in history if h['wasAnswered']]),
                    "correctAnswers": len([h for h in history if h['wasCorrect']]),
                    "recommendationAccuracy": int(len([h for h in history if h['wasCorrect']]) / max(len([h for h in history if h['wasAnswered']]), 1) * 100)
                }
            }
        })
        
    except Exception as e:
        print(f"❌ 获取推荐历史时发生错误: {e}")
        return jsonify({
            "code": 500,
            "message": f"服务器内部错误: {str(e)}",
            "data": None
        }), 500

if __name__ == '__main__':
    print("🚀 启动CSrecomMIND后端API服务...")
    print("📡 API服务地址: http://localhost:5000")
    print("📖 可用接口:")
    print("  - GET  /api/health - 健康检查")
    print("  - POST /api/student/recommend-questions - 获取推荐题目")
    print("  - POST /api/student/submit-answer - 提交答案")
    print("  - POST /api/student/get-explanation - 获取解析")
    print("  - GET  /api/student/weak-knowledge-points - 获取薄弱知识点")
    print("  - GET  /api/student/progress - 获取学习进展")
    print("  - POST /api/student/error-analysis - 获取错因分析")
    print("  - GET  /api/student/learning-analysis - 获取学习分析报告")
    print("  - GET  /api/student/recommendation-history - 获取推荐历史")
    print("\n🎯 功能特色:")
    print("  ✅ 智能推荐算法")
    print("  ✅ 实时学习分析")
    print("  ✅ 知识点掌握度追踪")
    print("  ✅ 薄弱知识点诊断")
    print("  ✅ 个性化学习路径")
    print("  ✅ 错因分析功能")
    print("  ✅ 学生数据库管理")
    print("  ✅ 学习模式分析")
    print("  ✅ 推荐效果追踪")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
