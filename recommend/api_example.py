#!/usr/bin/env python3
"""
API使用示例 - 展示如何在代码中使用推荐系统API
"""

from start import EducationRecommendationAPI

def api_demo():
    """API使用演示"""
    print("🚀 API使用演示开始")
    print("="*50)
    
    # 1. 初始化API
    api = EducationRecommendationAPI()
    
    # 2. 创建学生
    print("\n📝 1. 创建学生...")
    student_result = api.start_session("api_demo_student", {
        "K1": 0.3,  # 集合运算有一定基础
        "K2": 0.1,  # 关系映射较薄弱
        "K3": 0.2   # 图基本概念有所了解
    })
    print(f"   结果: {student_result['status']}")
    
    # 3. 获取推荐题目
    print("\n📝 2. 获取推荐题目...")
    questions_result = api.get_questions(2)
    if questions_result["status"] == "success":
        print(f"   推荐了 {len(questions_result['recommendations'])} 道题目")
        for i, q in enumerate(questions_result['recommendations']):
            print(f"   题目{i+1}: {q['qid']} - {q['content'][:30]}...")
    
    # 4. 模拟答题并提交
    print("\n📝 3. 提交答题结果...")
    if questions_result["status"] == "success":
        # 模拟学生答题
        student_answers = []
        for q in questions_result['recommendations']:
            # 模拟选择答案（这里选择C作为示例）
            student_answers.append({
                "qid": q["qid"],
                "selected": "C"
            })
        
        submit_result = api.submit_student_answers(student_answers)
        print(f"   提交结果: {submit_result['status']}")
        
        if submit_result["status"] == "success":
            print(f"   完成批次: {submit_result['batch_completed']}")
            if "answer_details" in submit_result:
                correct_count = sum(1 for detail in submit_result["answer_details"] if detail["correct"])
                print(f"   答对题目: {correct_count}/{len(submit_result['answer_details'])}")
    
    # 5. 获取薄弱知识点分析
    print("\n📝 4. 获取薄弱知识点分析...")
    weak_points_result = api.get_weak_points(0.4)
    if weak_points_result["status"] == "success":
        progress = weak_points_result["progress_summary"]
        print(f"   学习进展: 掌握{progress['mastered']}个，薄弱{progress['weak']}个")
        
        if weak_points_result["weak_knowledge_points"]:
            print(f"   最薄弱的3个知识点:")
            for kp, score in weak_points_result["weak_knowledge_points"][:3]:
                print(f"     {kp}: {score:.3f}")
    
    # 6. 检查答案功能演示
    print("\n📝 5. 独立答案检查功能...")
    check_answers = [
        {"qid": "Q1", "selected": "C"},  # 正确答案
        {"qid": "Q2", "selected": "A"},  # 可能错误
    ]
    check_result = api.check_answers_only(check_answers)
    if check_result["status"] == "success":
        print(f"   检查结果: {check_result['correct_count']}/{check_result['total_questions']} 正确")
        print(f"   准确率: {check_result['accuracy']:.1%}")
    
    # 7. 获取学生状态
    print("\n📝 6. 获取当前学生状态...")
    status_result = api.get_session_status()
    if status_result["status"] == "success":
        print(f"   学生ID: {status_result['student_id']}")
        print(f"   完成批次: {status_result['batch_count']}")
        print(f"   总题目数: {status_result['total_questions']}")
        print(f"   掌握知识点数: {len(status_result['mastered_knowledge_points'])}")
    
    # 8. 结束会话
    print("\n📝 7. 结束学习会话...")
    end_result = api.end_session()
    print(f"   结束结果: {end_result['status']}")
    
    print("\n🎉 API演示完成！")

def batch_answer_checking_demo():
    """批量答案检查演示"""
    print("\n" + "="*50)
    print("🔍 批量答案检查功能演示")
    print("="*50)
    
    api = EducationRecommendationAPI()
    
    # 准备一组答案进行检查
    test_answers = [
        {"qid": "Q1", "selected": "C"},   # 集合并集，正确答案应该是C
        {"qid": "Q2", "selected": "B"},   # 自反关系，需要检查
        {"qid": "Q3", "selected": "A"},   # 传递关系，需要检查
        {"qid": "Q7", "selected": "C"},   # 完全图边数，正确答案应该是C
    ]
    
    print("\n📋 检查以下答案:")
    for ans in test_answers:
        print(f"   {ans['qid']}: 选择 {ans['selected']}")
    
    result = api.check_answers_only(test_answers)
    
    if result["status"] == "success":
        print(f"\n📊 检查结果:")
        print(f"   总题目数: {result['total_questions']}")
        print(f"   正确题目: {result['correct_count']}")
        print(f"   准确率: {result['accuracy']:.1%}")
        
        print(f"\n📝 详细结果:")
        for detail in result["details"]:
            if detail.get("status") == "success":
                status_emoji = "✅" if detail["is_correct"] else "❌"
                print(f"   {detail['qid']}: {detail['selected']} {status_emoji}")
                if not detail["is_correct"]:
                    print(f"      正确答案: {detail['correct_answer']}")
            else:
                print(f"   错误: {detail.get('message', '未知错误')}")

if __name__ == "__main__":
    # 运行API演示
    api_demo()
    
    # 运行答案检查演示
    batch_answer_checking_demo()
