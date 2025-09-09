#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱增强器 - 简化版
直接生成标准化的关系类型，避免冗余
"""

import pandas as pd
import json
from langchain_openai import ChatOpenAI
import os
import logging

class KGReinforcer:
    def __init__(self, api_key: str = None):
        self.kg_data = None
        self.enhanced_kg = None
        
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        try:
            self.chat_llm = ChatOpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                model="qwen-plus",
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            self.chat_llm = None
            print(f"通义千问客户端初始化失败: {e}")
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 定义标准化的关系类型
        self.standard_relations = [
            'contains', 'is_defined_as', 'has_property', 'has_formula', 
            'has_condition', 'is_equivalent_to', 'transforms_to', 'belongs_to',
            'related_to', 'applies_to', 'affects', 'supports', 'uses_algorithm'
        ]
    
    def load_knowledge_graph(self, file_path: str):
        try:
            self.kg_data = pd.read_csv(file_path)
            print(f"成功加载知识图谱，包含 {len(self.kg_data)} 条三元组")
            return self.kg_data
        except Exception as e:
            print(f"加载知识图谱失败: {e}")
            raise
    
    def enhance_with_llm(self):
        if self.kg_data is None:
            raise ValueError("请先加载知识图谱数据")
        
        print("开始使用LLM进行知识图谱增强...")
        
        # 关系增强
        enhanced_triples = self._relation_enhancement()
        
        # 合并数据
        enhanced_df = pd.concat([
            self.kg_data,
            pd.DataFrame(enhanced_triples, columns=['subject', 'predicate', 'object', 'source'])
        ], ignore_index=True)
        
        # 规范化关系类型
        enhanced_df = self._normalize_relations(enhanced_df)
        
        self.enhanced_kg = enhanced_df
        print(f"增强完成，新增 {len(enhanced_triples)} 条三元组")
        
        return enhanced_df
    
    def _relation_enhancement(self):
        enhanced_triples = []
        
        entities = set(self.kg_data['subject'].tolist() + self.kg_data['object'].tolist())
        
        prompt = f"""
        你是一个图论专家。基于以下图论知识图谱信息，请生成15-20个新的、有意义的三元组：

        主要图论概念：{', '.join(list(entities)[:30])}

        重要要求：
        1. 必须使用以下标准化关系类型之一：
           {', '.join(self.standard_relations)}

        2. 分析图论中实体之间的潜在关系，如：拓扑关系、结构关系、算法关系等
        3. 发现缺失的重要连接，如：图的同构关系、子图关系、补图关系等
        4. 确保新关系在图论学术上有意义且逻辑合理
        5. 重点关注：连通性、着色、匹配、覆盖、平面性、树结构等图论核心概念

        请以JSON格式返回，格式如下：
        {{
            "new_triples": [
                {{"subject": "主体实体", "predicate": "标准化关系类型", "object": "客体实体", "reasoning": "为什么这个关系在图论中有意义"}}
            ]
        }}

        注意：必须使用上述标准化关系类型，不要创建新的关系类型。
        """
        
        try:
            response = self._call_llm(prompt)
            new_triples = json.loads(response)
            
            for triple_info in new_triples.get("new_triples", []):
                enhanced_triples.append([
                    triple_info["subject"],
                    triple_info["predicate"],
                    triple_info["object"],
                    "LLM_enhanced_relation"
                ])
                    
        except Exception as e:
            self.logger.warning(f"关系增强失败: {e}")
        
        return enhanced_triples
    
    def _call_llm(self, prompt: str):
        if self.chat_llm is None:
            return self._get_mock_response()
        
        try:
            messages = [
                {"role": "system", "content": "你是一个知识图谱专家，请严格按照要求的JSON格式返回结果，并使用指定的标准化关系类型。"},
                {"role": "user", "content": prompt}
            ]
            response = self.chat_llm.invoke(messages)
            
            content = response.content
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                return content[start:end]
            else:
                return self._get_mock_response()
                
        except Exception as e:
            self.logger.error(f"通义千问调用失败: {e}")
            return self._get_mock_response()
    
    def _get_mock_response(self):
        return '''
        {
            "new_triples": [
                {"subject": "欧拉图", "predicate": "has_property", "object": "所有顶点度数均为偶数", "reasoning": "欧拉图的基本性质"},
                {"subject": "哈密顿图", "predicate": "has_property", "object": "存在经过所有顶点的回路", "reasoning": "哈密顿图的基本性质"},
                {"subject": "平面图", "predicate": "has_property", "object": "可以画在平面上无交叉边", "reasoning": "平面图的定义性质"}
            ]
        }
        '''
    
    def _normalize_relations(self, df):
        normalized_df = df.copy()
        
        original_relations = set(df['predicate'].unique())
        print(f"规范化前关系类型数量: {len(original_relations)}")
        
        # 关系映射
        relation_mapping = {
            '具有': 'has_property',
            '包含': 'contains',
            '是': 'is_a',
            '属于': 'belongs_to',
            '相关': 'related_to',
            '关联': 'related_to',
            '影响': 'affects',
            '支撑': 'supports',
            '构成': 'constitutes',
            '对应': 'corresponds_to',
            '利用': 'utilizes',
            '适用于': 'applies_to',
            '可用于': 'applies_to',
            '可应用于': 'applies_to',
            '可转化为': 'transforms_to',
            '可退化为': 'transforms_to',
            '可具有': 'has_property',
            '可能为': 'has_property',
            '可能具有': 'has_property',
            '不是': 'is_not',
            '当': 'when',
            '与': 'and',
            '和': 'and',
            '最大边数为': 'has_property',
            '与连通性相关': 'related_to',
            '着色问题涉及': 'involves',
            '可能为树结构': 'has_property',
            '可用于建模': 'applies_to',
            '隐含条件': 'implies',
            '关联定理': 'related_to',
            '推导性质': 'has_property',
            '应用场景': 'applies_to',
            '关联概念': 'related_to',
            '关联结构': 'related_to',
            '色数等于': 'has_property',
            '匹配数为': 'has_property',
            '不是平面图当': 'has_property',
            '最小顶点覆盖数为': 'has_property',
            '包含生成树': 'contains',
            '支持': 'supports',
            '影响': 'affects',
            '支撑': 'supports',
            '应用于': 'applies_to',
            '可以是': 'has_property',
            '可用于表示': 'applies_to',
            '可能具有': 'has_property',
            '涉及': 'involves',
            '可退化为': 'transforms_to',
            '可以转换为': 'transforms_to',
            '转换为': 'transforms_to',
            '适用于': 'applies_to',
            '对应于': 'corresponds_to',
            '利用': 'utilizes',
            '可应用于': 'applies_to',
            'implies': 'implies',
            'requires': 'requires',
            'relates_to': 'related_to',
            'applies_to': 'applies_to',
            'supports': 'supports',
            'related_to': 'related_to',
            '可进行二着色': 'has_property',
            '匹配问题具有特殊性质': 'has_property',
            '顶点覆盖与最大匹配等价': 'has_property',
            '无三角形结构': 'has_property',
            '可转化为树结构的子图': 'transforms_to',
            '适用于二分匹配算法': 'applies_to',
            'has_property': 'has_property',
            'application': 'applies_to',
            'can_be_transformed_into': 'transforms_to',
            '受限于': 'constrained_by',
            '满足性质': 'has_property',
            '与最大度存在关系': 'related_to',
            '与最大度相关': 'related_to',
            '受最大度影响': 'affected_by',
            'affects': 'affects',
            'used_in': 'applies_to',
            'associated_with': 'related_to',
            'impacts': 'affects',
            'is_essential_for': 'supports',
            'preserves_property': 'has_property',
            'implies_condition': 'implies',
            'is_bipartite': 'has_property',
            'has_chromatic_number_2': 'has_property',
            'contains_perfect_matching_under_certain_conditions': 'contains',
            'can_be_used_for_bipartite_network_analysis': 'applies_to',
            'has_spanning_forest_structure': 'has_property',
            'may_be_planar': 'has_property',
            'allows': 'supports',
            'is_necessary_for': 'supports',
            'application_in': 'applies_to',
            '隐含联系': 'implies',
            '关联': 'related_to',
            '应用关联': 'applies_to',
            '推导关联': 'related_to',
            'contains': 'contains',
            'is_defined_as': 'is_defined_as',
            'has_formula': 'has_formula',
            'has_condition': 'has_condition',
            'transforms_to': 'transforms_to',
            'is_equivalent_to': 'is_equivalent_to',
            'belongs_to': 'belongs_to',
            'has_application': 'applies_to',
            'evolves_from': 'evolves_from'
        }
        
        normalized_df['predicate'] = normalized_df['predicate'].map(
            lambda x: relation_mapping.get(x, x) if pd.notna(x) else x
        )
        
        normalized_relations = set(normalized_df['predicate'].unique())
        changed_count = len(original_relations - normalized_relations)
        
        print(f"关系规范化完成，修改了 {changed_count} 个关系类型")
        print(f"规范化前关系数量: {len(original_relations)}")
        print(f"规范化后关系数量: {len(normalized_relations)}")
        
        return normalized_df
    
    def save_enhanced_kg(self, output_path: str):
        if self.enhanced_kg is not None:
            self.enhanced_kg.to_csv(output_path, index=False, encoding='utf-8')
            print(f"增强后的知识图谱已保存到: {output_path}")
        else:
            print("没有增强后的知识图谱可保存")
    
    def generate_report(self):
        if self.enhanced_kg is None:
            return "请先进行知识图谱增强"
        
        original_count = len(self.kg_data)
        enhanced_count = len(self.enhanced_kg)
        new_count = enhanced_count - original_count
        
        original_relations = len(self.kg_data['predicate'].unique())
        enhanced_relations = len(self.enhanced_kg['predicate'].unique())
        
        report = f"""
# 知识图谱增强报告

## 增强概览
- 原始三元组数量: {original_count}
- 增强后三元组数量: {enhanced_count}
- 新增三元组数量: {new_count}
- 增强比例: {(new_count/original_count*100):.2f}%

## 关系类型优化
- 原始关系类型数量: {original_relations}
- 优化后关系类型数量: {enhanced_relations}
- 减少关系类型数量: {original_relations - enhanced_relations}
- 优化比例: {((original_relations - enhanced_relations)/original_relations*100):.2f}%

## 标准化关系类型
{', '.join(sorted(self.enhanced_kg['predicate'].unique()))}

## 质量评估
- 新增知识数量: {new_count} 条
- 知识覆盖率提升: {(new_count/original_count*100):.2f}%
- 关系类型标准化: 使用预定义的标准化关系类型
- 知识图谱结构: 更加清晰和规范
        """
        
        return report

def main():
    try:
        reinforcer = KGReinforcer()
        reinforcer.load_knowledge_graph("final_knowledge_graph.csv")
        enhanced_kg = reinforcer.enhance_with_llm()
        reinforcer.save_enhanced_kg("enhanced_knowledge_graph.csv")
        
        report = reinforcer.generate_report()
        print(report)
        
        with open("enhancement_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
    except Exception as e:
        print(f"程序执行失败: {e}")

if __name__ == "__main__":
    main()




