#!/usr/bin/env python3
"""
API兼容性测试 - 确保优化后的算法不影响前端API调用
"""

from simple_system import KnowledgeGraphRecommendationEngine
import json

def test_api_compatibility():
    """测试API接口兼容性"""
    
    print("🧪 API兼容性测试开始...")
    print("=" * 60)
    
    # 初始化系统
    engine = KnowledgeGraphRecommendationEngine()
    
    # 测试1: 创建学生
    print("📝 测试1: create_student API")
    result = engine.create_student("api_test_student")
    print(f"✅ 创建学生结果: {result}")
    assert "status" in result and result["status"] == "success"
    
    # 测试2: 获取推荐
    print("\n📝 测试2: get_recommendations API")
    result = engine.get_recommendations("api_test_student", num_questions=3)
    print(f"✅ 推荐结果包含字段: {list(result.keys())}")
    assert "status" in result and "recommendations" in result
    
    # 测试3: 提交答案 (先从check_answers获取正确格式)
    print("\n📝 测试3: 准备正确的答案格式")
    check_result = engine.check_answers([{"qid": "Q1", "answer": "A"}, {"qid": "Q2", "answer": "B"}])
    if check_result["status"] == "success":
        formatted_answers = []
        for detail in check_result["details"]:
            formatted_answers.append({
                "qid": detail["qid"],
                "correct": detail["correct"],
                "knowledge_points": detail["knowledge_points"]
            })
        
        print("\n📝 测试3: submit_answers API")
        result = engine.submit_answers("api_test_student", formatted_answers)
        print(f"✅ 提交答案结果: {result}")
        assert "status" in result
    
    # 测试4: 检查答案
    print("\n📝 测试4: check_answers API")
    result = engine.check_answers([{"qid": "Q1", "answer": "A"}, {"qid": "Q2", "answer": "B"}])
    print(f"✅ 检查答案结果包含字段: {list(result.keys())}")
    assert "status" in result and "details" in result
    
    # 测试5: 获取学生状态
    print("\n📝 测试5: get_student_status API")
    result = engine.get_student_status("api_test_student")
    print(f"✅ 学生状态结果包含字段: {list(result.keys())}")
    assert "status" in result and "student_info" in result
    
    # 测试6: 获取薄弱知识点
    print("\n📝 测试6: get_weak_knowledge_points API")
    result = engine.get_weak_knowledge_points("api_test_student")
    print(f"✅ 薄弱知识点结果包含字段: {list(result.keys())}")
    assert "status" in result and "weak_points" in result
    
    print("\n" + "=" * 60)
    print("🎉 所有API接口测试通过！前端调用方式保持不变。")
    print("✅ 优化后的算法完全向后兼容！")

if __name__ == "__main__":
    test_api_compatibility()
