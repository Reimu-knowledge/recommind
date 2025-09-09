#!/usr/bin/env python3
"""
API返回值格式示例文件
展示所有API方法的典型返回值格式，方便前端开发者参考
"""

import json

# API返回值示例
API_RESPONSE_EXAMPLES = {
    
    "start_session": {
        "success": {
            "status": "success",
            "student_id": "student_001", 
            "initial_mastery": {
                "K1": 0.1,
                "K2": 0.1,
                "K3": 0.05
            },
            "message": "学生 student_001 创建成功"
        },
        "error": {
            "status": "error",
            "message": "学生 student_001 已存在"
        }
    },
    
    "get_questions": {
        "success": {
            "status": "success",
            "student_id": "student_001",
            "recommendations": [
                {
                    "qid": "Q1",
                    "content": "集合A={1,2,3}，集合B={2,3,4}，求A∪B",
                    "options": [
                        "{1,2,3}",
                        "{2,3}", 
                        "{1,2,3,4}",
                        "{4}"
                    ],
                    "knowledge_points": {
                        "K1": 0.9
                    },
                    "difficulty": 0.5
                },
                {
                    "qid": "Q7",
                    "content": "有n个顶点的完全图有多少条边？",
                    "options": [
                        "n",
                        "n-1",
                        "n(n-1)/2",
                        "n²"
                    ],
                    "knowledge_points": {
                        "K3": 0.6,
                        "K8": 0.4
                    },
                    "difficulty": 0.5
                }
            ],
            "batch_number": 1
        },
        "error": {
            "status": "error",
            "message": "学生 student_001 不存在"
        }
    },
    
    "submit_student_answers": {
        "success": {
            "status": "success",
            "student_id": "student_001",
            "batch_completed": 1,
            "current_mastery": {
                "K1": 0.370,
                "K2": 0.100,
                "K3": 0.530,
                "K8": 0.180
            },
            "mastered_knowledge_points": ["K3"],
            "answer_details": [
                {
                    "qid": "Q1",
                    "correct": True,
                    "knowledge_points": {"K1": 0.9},
                    "selected": "C",
                    "correct_answer": "{1,2,3,4}"
                },
                {
                    "qid": "Q7", 
                    "correct": True,
                    "knowledge_points": {"K3": 0.6, "K8": 0.4},
                    "selected": "C",
                    "correct_answer": "n(n-1)/2"
                }
            ]
        },
        "error": {
            "status": "error",
            "message": "答案格式错误，需要包含字段: ['qid', 'selected']"
        }
    },
    
    "check_answers_only": {
        "success": {
            "status": "success",
            "total_questions": 3,
            "correct_count": 2,
            "accuracy": 0.6666666666666666,
            "details": [
                {
                    "status": "success",
                    "qid": "Q1",
                    "selected": "C",
                    "selected_option": "{1,2,3,4}",
                    "correct_answer": "{1,2,3,4}",
                    "is_correct": True,
                    "knowledge_points": {"K1": 0.9}
                },
                {
                    "status": "success", 
                    "qid": "Q2",
                    "selected": "B",
                    "selected_option": "R={(2,2)}",
                    "correct_answer": "R={(1,1),(2,2)}",
                    "is_correct": False,
                    "knowledge_points": {"K2": 0.8}
                },
                {
                    "status": "success",
                    "qid": "Q7",
                    "selected": "C",
                    "selected_option": "n(n-1)/2",
                    "correct_answer": "n(n-1)/2",
                    "is_correct": True,
                    "knowledge_points": {"K3": 0.6, "K8": 0.4}
                }
            ]
        },
        "error": {
            "status": "error",
            "message": "题目 Q99 不存在"
        }
    },
    
    "get_weak_points": {
        "success": {
            "status": "success",
            "student_id": "student_001",
            "weak_knowledge_points": [
                ["K2", 0.100],
                ["K8", 0.180],
                ["K6", 0.250]
            ],
            "progress_summary": {
                "total_knowledge_points": 5,
                "mastered": 1,
                "moderate": 1,
                "weak": 3,
                "mastered_list": ["K3"],
                "weak_list": ["K2", "K8", "K6"],
                "average_mastery": 0.26
            },
            "recommendations": [
                "🔴 K2 掌握度极低(0.10)，建议重点学习基础概念",
                "🟡 K8 掌握度较低(0.18)，需要加强练习",
                "🟠 K6 掌握度一般(0.25)，可以适量练习巩固",
                "💡 建议：薄弱知识点较多，建议循序渐进，先攻克最薄弱的2-3个知识点"
            ]
        },
        "error": {
            "status": "error",
            "message": "学生 student_001 不存在"
        }
    },
    
    "get_session_status": {
        "success": {
            "status": "success",
            "student_id": "student_001",
            "batch_count": 2,
            "total_questions": 5,
            "mastery_scores": {
                "K1": 0.370,
                "K2": 0.100,
                "K3": 0.530,
                "K8": 0.180,
                "K6": 0.250
            },
            "mastered_knowledge_points": ["K3"],
            "vector_norm": 1.0
        },
        "error": {
            "status": "error",
            "message": "没有活跃的学习会话"
        }
    },
    
    "end_session": {
        "success": {
            "status": "success",
            "message": "会话 student_001 已成功结束",
            "final_status": {
                "status": "success",
                "student_id": "student_001",
                "batch_count": 3,
                "total_questions": 8,
                "mastery_scores": {
                    "K1": 0.450,
                    "K2": 0.200,
                    "K3": 0.650,
                    "K8": 0.280,
                    "K6": 0.350
                },
                "mastered_knowledge_points": ["K3"],
                "vector_norm": 1.0
            }
        },
        "error": {
            "status": "error",
            "message": "没有活跃的学习会话"
        }
    }
}

def print_api_examples():
    """打印所有API返回值示例"""
    print("🔧 知识图谱推荐系统 API 返回值格式示例")
    print("="*60)
    
    for api_name, examples in API_RESPONSE_EXAMPLES.items():
        print(f"\n📝 {api_name.upper()}")
        print("-" * 40)
        
        print("✅ 成功响应:")
        print(json.dumps(examples["success"], indent=2, ensure_ascii=False))
        
        print("\n❌ 错误响应:")
        print(json.dumps(examples["error"], indent=2, ensure_ascii=False))
        print()

def get_example(api_name, response_type="success"):
    """获取特定API的示例响应
    
    Args:
        api_name: API方法名
        response_type: "success" 或 "error"
    
    Returns:
        示例响应字典
    """
    if api_name in API_RESPONSE_EXAMPLES:
        return API_RESPONSE_EXAMPLES[api_name].get(response_type)
    return None

def save_examples_to_file(filename="api_response_examples.json"):
    """将所有示例保存到JSON文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(API_RESPONSE_EXAMPLES, f, indent=2, ensure_ascii=False)
    print(f"✅ API示例已保存到 {filename}")

if __name__ == "__main__":
    # 打印所有示例
    print_api_examples()
    
    # 保存到文件
    save_examples_to_file()
    
    print("\n💡 使用方法:")
    print("from api_response_examples import get_example")
    print("success_example = get_example('start_session', 'success')")
    print("error_example = get_example('start_session', 'error')")
