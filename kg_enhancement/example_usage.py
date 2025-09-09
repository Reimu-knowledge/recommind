#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱增强器使用示例
使用通义千问大模型增强知识图谱
"""

import os
from KGReinforcer import KGReinforcer
import json

def main():
    """主函数示例"""
    
    # 方法1: 直接设置API密钥
    # api_key = "your-dashscope-api-key-here"
    # reinforcer = KGReinforcer(api_key=api_key)
    
    # 方法2: 从环境变量获取API密钥
    reinforcer = KGReinforcer(api_key="sk-c39ae8196c154979bc958d0dde69633b")
    
    print("=== 知识图谱增强器示例 ===")
    print("使用通义千问大模型进行知识图谱增强")
    print()
    
    try:
        # 1. 加载知识图谱
        print("1. 加载知识图谱...")
        reinforcer.load_knowledge_graph("final_knowledge_graph.csv")
        print("✓ 知识图谱加载成功")
        print()
        
        # 2. 分析知识图谱结构
        print("2. 分析知识图谱结构...")
        analysis = reinforcer.analyze_kg_structure()
        print("知识图谱结构分析结果:")
        print(f"  - 总三元组数量: {analysis['total_triples']}")
        print(f"  - 唯一实体数量: {analysis['unique_entities']}")
        print(f"  - 关系类型数量: {analysis['unique_relations']}")
        print(f"  - 主要关系类型: {list(analysis['relation_types'].keys())[:5]}")
        print()
        
        # 3. 进行关系增强
        print("3. 进行关系增强...")
        relation_enhanced = reinforcer.enhance_with_llm("relation")
        print(f"✓ 关系增强完成，新增 {len(relation_enhanced) - len(reinforcer.kg_data)} 条三元组")
        print()
        
        # 4. 进行实体增强
        print("4. 进行实体增强...")
        entity_enhanced = reinforcer.enhance_with_llm("entity")
        print(f"✓ 实体增强完成，新增 {len(entity_enhanced) - len(relation_enhanced)} 条三元组")
        print()
        
        # 5. 进行推理增强
        print("5. 进行推理增强...")
        reasoning_enhanced = reinforcer.enhance_with_llm("reasoning")
        print(f"✓ 推理增强完成，新增 {len(reasoning_enhanced) - len(entity_enhanced)} 条三元组")
        print()
        
        # 6. 构建图对象
        print("6. 构建图对象...")
        graph = reinforcer.build_graph()
        print(f"✓ 图对象构建完成，包含 {len(graph.nodes())} 个节点和 {len(graph.edges())} 条边")
        print()
        
        # 7. 生成增强报告
        print("7. 生成增强报告...")
        report = reinforcer.generate_report()
        print("增强报告:")
        print(report)
        print()
        
        # 8. 保存增强后的知识图谱
        print("8. 保存增强结果...")
        reinforcer.save_enhanced_kg("enhanced_knowledge_graph.csv")
        print("✓ 增强后的知识图谱已保存")
        
        # 9. 保存增强报告
        with open("enhancement_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("✓ 增强报告已保存到 enhancement_report.md")
        
        print("\n=== 增强完成 ===")
        print("所有增强操作已成功完成！")
        
    except Exception as e:
        print(f"❌ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()

def test_llm_connection():
    """测试通义千问连接"""
    print("测试通义千问连接...")
    
    try:
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("❌ 未设置DASHSCOPE_API_KEY环境变量")
            return False
        
        chat_llm = ChatOpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus",
            temperature=0.7,
            max_tokens=100
        )
        
        messages = [
            {"role": "system", "content": "你是一个知识图谱专家。"},
            {"role": "user", "content": "请简单介绍一下知识图谱增强的概念"}
        ]
        
        response = chat_llm.invoke(messages)
        print("✓ 通义千问连接成功")
        print(f"响应内容: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 通义千问连接失败: {e}")
        return False

if __name__ == "__main__":
    # 直接运行主程序，因为API密钥已经在代码中设置
    print("\n开始知识图谱增强...")
    main()
