#!/usr/bin/env python3
"""
错因分析接口测试脚本
"""

import requests
import json
import time

class ErrorAnalysisTester:
    """错因分析测试类"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def test_single_option_analysis(self, question_id: str, option_letter: str) -> bool:
        """测试单个选项的错因分析"""
        print(f"🔍 测试错因分析: {question_id}-{option_letter}")
        try:
            response = self.session.get(f"{self.base_url}/api/error-analysis/{question_id}/{option_letter}")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data['data']
                
                print(f"✅ 错因分析获取成功:")
                print(f"   题目: {analysis['question_id']}")
                print(f"   选择选项: {analysis['selected_option']}")
                print(f"   需要巩固的知识点数量: {len(analysis['knowledge_points_to_review'])}")
                
                # 显示需要巩固的知识点
                if analysis['knowledge_points_to_review']:
                    print(f"   需要巩固的知识点:")
                    for kp in analysis['knowledge_points_to_review']:
                        priority_icon = "🔴" if kp['priority'] == 'high' else "🟡"
                        print(f"     {priority_icon} {kp['knowledge_point']} (相似度: {kp['similarity']:.3f})")
                else:
                    print(f"   ✅ 没有需要特别巩固的知识点")
                
                return True
            else:
                print(f"❌ 错因分析获取失败: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 错因分析获取异常: {e}")
            return False
    
    def test_complete_question_analysis(self, question_id: str) -> bool:
        """测试题目的完整错因分析"""
        print(f"📋 测试完整错因分析: {question_id}")
        try:
            response = self.session.get(f"{self.base_url}/api/error-analysis/{question_id}")
            
            if response.status_code == 200:
                data = response.json()
                analysis = data['data']
                
                print(f"✅ 完整错因分析获取成功:")
                print(f"   题目: {analysis['question_text'][:50]}...")
                print(f"   选项分析:")
                
                for option_letter, option_analysis in analysis['options_analysis'].items():
                    print(f"     选项{option_letter}: {option_analysis['option_text']}")
                    print(f"       需要巩固的知识点数量: {option_analysis['review_count']}")
                    
                    # 显示需要巩固的知识点
                    if option_analysis['knowledge_points_to_review']:
                        for kp in option_analysis['knowledge_points_to_review'][:3]:  # 只显示前3个
                            print(f"         - {kp['knowledge_point']} (相似度: {kp['similarity']:.3f})")
                    else:
                        print(f"         ✅ 没有需要特别巩固的知识点")
                
                return True
            else:
                print(f"❌ 完整错因分析获取失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 完整错因分析获取异常: {e}")
            return False
    
    def test_error_cases(self) -> bool:
        """测试错误情况"""
        print(f"🚫 测试错误情况")
        
        # 测试不存在的题目
        print("   测试不存在的题目...")
        try:
            response = self.session.get(f"{self.base_url}/api/error-analysis/Q999/A")
            if response.status_code == 404:
                print("   ✅ 不存在题目正确返回404")
            else:
                print(f"   ❌ 不存在题目返回错误状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 测试不存在题目异常: {e}")
            return False
        
        # 测试不存在的选项
        print("   测试不存在的选项...")
        try:
            response = self.session.get(f"{self.base_url}/api/error-analysis/Q1/E")
            if response.status_code == 404:
                print("   ✅ 不存在选项正确返回404")
            else:
                print(f"   ❌ 不存在选项返回错误状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ 测试不存在选项异常: {e}")
            return False
        
        return True
    
    def run_comprehensive_test(self) -> bool:
        """运行综合测试"""
        print("🧪 错因分析接口综合测试")
        print("=" * 60)
        
        # 测试用例
        test_cases = [
            ("Q1", "A"),  # 握手定理相关
            ("Q1", "B"),  # 握手定理相关
            ("Q2", "A"),  # 强连通图相关
            ("Q2", "C"),  # 强连通图相关
        ]
        
        success_count = 0
        
        # 1. 测试单个选项分析
        print("📝 测试单个选项错因分析")
        print("-" * 30)
        for question_id, option_letter in test_cases:
            if self.test_single_option_analysis(question_id, option_letter):
                success_count += 1
            print()
        
        # 2. 测试完整题目分析
        print("📋 测试完整题目错因分析")
        print("-" * 30)
        test_questions = ["Q1", "Q2"]
        for question_id in test_questions:
            if self.test_complete_question_analysis(question_id):
                success_count += 1
            print()
        
        # 3. 测试错误情况
        print("🚫 测试错误情况")
        print("-" * 30)
        if self.test_error_cases():
            success_count += 1
        print()
        
        # 4. 测试大小写兼容性
        print("🔤 测试大小写兼容性")
        print("-" * 30)
        if self.test_single_option_analysis("Q1", "a"):  # 小写
            success_count += 1
        print()
        
        total_tests = len(test_cases) + len(test_questions) + 3  # 错误测试 + 大小写测试
        success_rate = success_count / total_tests
        
        print("📊 测试结果统计")
        print("-" * 30)
        print(f"   总测试数: {total_tests}")
        print(f"   成功数: {success_count}")
        print(f"   成功率: {success_rate:.2%}")
        
        if success_rate >= 0.8:
            print("✅ 错因分析接口测试通过！")
            return True
        else:
            print("❌ 错因分析接口测试失败！")
            return False

def main():
    """主函数"""
    print("🔍 错因分析接口测试工具")
    print("=" * 60)
    
    # 等待服务启动
    print("⏳ 等待服务启动...")
    time.sleep(2)
    
    # 创建测试器
    tester = ErrorAnalysisTester()
    
    # 运行综合测试
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🎉 错因分析接口测试完成！")
        print("💡 接口功能:")
        print("   - 根据题目ID和选项获取错因分析")
        print("   - 提供知识点相似度分析")
        print("   - 生成个性化学习建议")
        print("   - 支持完整题目分析")
        print("   - 完善的错误处理")
    else:
        print("\n❌ 错因分析接口测试失败！")
        print("💡 请检查:")
        print("   - 后端服务是否正常启动")
        print("   - 错因分析数据文件是否存在")
        print("   - 数据格式是否正确")

if __name__ == "__main__":
    main()
