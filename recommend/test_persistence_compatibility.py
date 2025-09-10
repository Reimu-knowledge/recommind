#!/usr/bin/env python3
"""
新增数据持久化API兼容性测试
确保新功能不影响现有API的正常使用
"""

from start import EducationRecommendationAPI

def test_api_compatibility_with_persistence():
    """测试新API与现有API的兼容性"""
    print("🧪 数据持久化API兼容性测试")
    print("=" * 60)
    
    api = EducationRecommendationAPI()
    
    # 测试1: 原有API功能正常
    print("\n📝 测试1: 原有API功能正常...")
    
    # 创建学生
    result = api.start_session("test_student", {"K1": 0.2, "K2": 0.1, "K3": 0.15})
    assert result["status"] == "success", "创建学生失败"
    print("   ✅ 创建学生功能正常")
    
    # 获取推荐
    result = api.get_questions(2)
    assert result["status"] == "success", "获取推荐失败"
    print("   ✅ 推荐功能正常")
    
    # 提交答案
    answers = [{"qid": "Q1", "selected": "A"}, {"qid": "Q2", "selected": "B"}]
    result = api.submit_student_answers(answers)
    assert result["status"] == "success", "提交答案失败"
    print("   ✅ 答案提交功能正常")
    
    # 获取状态
    result = api.get_session_status()
    assert result["status"] == "success", "获取状态失败"
    print("   ✅ 状态查询功能正常")
    
    # 测试2: 新API功能正常
    print("\n📝 测试2: 新增持久化API功能正常...")
    
    # 导出学生数据
    result = api.export_student_data("test_student")
    assert result["status"] == "success", "导出学生数据失败"
    student_data = result["data"]
    print("   ✅ 学生数据导出功能正常")
    
    # 获取学生列表
    result = api.get_students_list()
    assert result["status"] == "success", "获取学生列表失败"
    assert result["total_count"] == 1, "学生数量不正确"
    print("   ✅ 学生列表功能正常")
    
    # 导出所有学生数据
    result = api.export_all_students()
    assert result["status"] == "success", "导出所有学生数据失败"
    all_students_data = result["data"]
    print("   ✅ 批量导出功能正常")
    
    # 测试3: 数据持久化循环测试
    print("\n📝 测试3: 数据持久化循环测试...")
    
    # 清空数据
    result = api.clear_all_students()
    assert result["status"] == "success", "清空数据失败"
    print("   ✅ 数据清空功能正常")
    
    # 验证数据已清空
    result = api.get_students_list()
    assert result["total_count"] == 0, "数据未完全清空"
    print("   ✅ 数据清空验证通过")
    
    # 恢复单个学生数据
    result = api.import_student_data(student_data)
    assert result["status"] == "success", "恢复学生数据失败"
    print("   ✅ 单个学生数据恢复功能正常")
    
    # 验证恢复的学生可以正常使用
    api.current_session = "test_student"
    result = api.get_session_status()
    assert result["status"] == "success", "恢复的学生状态异常"
    print("   ✅ 恢复的学生功能正常")
    
    # 继续学习测试
    result = api.get_questions(1)
    assert result["status"] == "success", "恢复的学生无法获取推荐"
    print("   ✅ 恢复的学生推荐功能正常")
    
    # 测试4: 批量数据恢复
    print("\n📝 测试4: 批量数据恢复测试...")
    
    # 清空数据
    api.clear_all_students()
    
    # 批量恢复
    result = api.import_all_students(all_students_data)
    assert result["status"] == "success", "批量恢复数据失败"
    print("   ✅ 批量数据恢复功能正常")
    
    # 验证恢复结果
    result = api.get_students_list()
    assert result["total_count"] == 1, "批量恢复的学生数量不正确"
    print("   ✅ 批量恢复验证通过")
    
    # 测试5: 文件持久化功能
    print("\n📝 测试5: 文件持久化功能测试...")
    
    # 保存到文件
    result = api.save_student_to_file("test_student", "test_persistence.json")
    assert result["status"] == "success", "保存到文件失败"
    print("   ✅ 文件保存功能正常")
    
    # 从文件加载
    api.clear_all_students()
    result = api.load_student_from_file("test_persistence.json")
    assert result["status"] == "success", "从文件加载失败"
    print("   ✅ 文件加载功能正常")
    
    # 清理测试文件
    import os
    try:
        os.remove("test_persistence.json")
        print("   🧹 测试文件已清理")
    except:
        pass
    
    # 结束会话
    api.end_session()
    
    print("\n🎉 所有兼容性测试通过！")
    print("=" * 60)
    print("📋 测试结果总结:")
    print("   ✅ 现有API功能完全正常")
    print("   ✅ 新增持久化API功能正常")
    print("   ✅ 数据导出/导入循环正常")
    print("   ✅ 文件持久化功能正常")
    print("   ✅ API之间无冲突，完全兼容")

if __name__ == "__main__":
    try:
        test_api_compatibility_with_persistence()
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
