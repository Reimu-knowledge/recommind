#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关系规范化工具
将知识图谱中的中英文混合关系统一为英文标准关系
"""

import pandas as pd
import json
from typing import Dict, Set

class RelationNormalizer:
    """关系规范化器"""
    
    def __init__(self):
        # 关系映射字典：中文/混合 -> 英文标准
        self.relation_mapping = {
            # 基础关系
            '具有': 'has_property',
            '包含': 'contains',
            '是': 'is_a',
            '属于': 'belongs_to',
            '相关': 'related_to',
            '关联': 'associated_with',
            '影响': 'affects',
            '支撑': 'supports',
            '构成': 'constitutes',
            '对应': 'corresponds_to',
            '利用': 'utilizes',
            '适用于': 'applies_to',
            '可用于': 'can_be_used_for',
            '可应用于': 'can_be_applied_to',
            '可转化为': 'can_be_transformed_into',
            '可退化为': 'can_degenerate_to',
            '可具有': 'can_have',
            '可能为': 'may_be',
            '可能具有': 'may_have',
            '不是': 'is_not',
            '当': 'when',
            '与': 'and',
            '和': 'and',
            
            # 图论专业关系
            '最大边数为': 'has_max_edges',
            '与连通性相关': 'related_to_connectivity',
            '着色问题涉及': 'involves_coloring',
            '可能为树结构': 'may_be_tree_structure',
            '可用于建模': 'can_model',
            '隐含条件': 'implies_condition',
            '关联定理': 'related_theorem',
            '推导性质': 'derived_property',
            '应用场景': 'application_scenario',
            '关联概念': 'related_concept',
            '关联结构': 'related_structure',
            '色数等于': 'chromatic_number_equals',
            '匹配数为': 'matching_number_equals',
            '不是平面图当': 'not_planar_when',
            '最小顶点覆盖数为': 'min_vertex_cover_equals',
            '包含生成树': 'contains_spanning_tree',
            '支持': 'supports',
            '影响': 'affects',
            '支撑': 'supports',
            '应用于': 'applied_in',
            '可以是': 'can_be',
            '可用于表示': 'can_represent',
            '涉及': 'involves',
            '可退化为': 'can_degenerate_to',
            '可以转换为': 'can_convert_to',
            '转换为': 'converts_to',
            '对应于': 'corresponds_to',
            '可进行二着色': 'can_be_bicolored',
            '匹配问题具有特殊性质': 'matching_problem_has_special_properties',
            '顶点覆盖与最大匹配等价': 'vertex_cover_equals_max_matching',
            '无三角形结构': 'no_triangle_structure',
            '可转化为树结构的子图': 'can_transform_to_tree_subgraph',
            '适用于二分匹配算法': 'suitable_for_bipartite_matching_algorithm',
            '受限于': 'constrained_by',
            '满足性质': 'satisfies_property',
            '与最大度存在关系': 'related_to_max_degree',
            '与最大度相关': 'related_to_max_degree',
            '受最大度影响': 'affected_by_max_degree',
            '隐含联系': 'implicit_connection',
            '应用关联': 'application_relation',
            '推导关联': 'derivation_relation',
            
            # 保持原有的英文关系
            'contains': 'contains',
            'is_defined_as': 'is_defined_as',
            'has_formula': 'has_formula',
            'has_condition': 'has_condition',
            'has_property': 'has_property',
            'transforms_to': 'transforms_to',
            'is_equivalent_to': 'is_equivalent_to',
            'belongs_to': 'belongs_to',
            'related_to': 'related_to',
            'has_application': 'has_application',
            'evolves_from': 'evolves_from',
            'implies': 'implies',
            'requires': 'requires',
            'relates_to': 'relates_to',
            'applies_to': 'applies_to',
            'supports': 'supports',
            'affects': 'affects',
            'used_in': 'used_in',
            'associated_with': 'associated_with',
            'impacts': 'impacts',
            'is_essential_for': 'is_essential_for',
            'preserves_property': 'preserves_property',
            'implies_condition': 'implies_condition',
            'is_bipartite': 'is_bipartite',
            'has_chromatic_number_2': 'has_chromatic_number_2',
            'contains_perfect_matching_under_certain_conditions': 'contains_perfect_matching_under_certain_conditions',
            'can_be_used_for_bipartite_network_analysis': 'can_be_used_for_bipartite_network_analysis',
            'has_spanning_forest_structure': 'has_spanning_forest_structure',
            'may_be_planar': 'may_be_planar',
            'allows': 'allows',
            'is_necessary_for': 'is_necessary_for',
            'application_in': 'application_in',
            'application': 'application',
            'can_be_transformed_into': 'can_be_transformed_into'
        }
    
    def normalize_kg(self, input_file: str, output_file: str = None) -> pd.DataFrame:
        """
        规范化知识图谱文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径（可选）
            
        Returns:
            规范化后的DataFrame
        """
        print(f"正在加载知识图谱: {input_file}")
        df = pd.read_csv(input_file)
        
        print(f"原始数据: {len(df)} 条三元组")
        print(f"原始关系类型数量: {len(df['predicate'].unique())}")
        
        # 显示原始关系类型
        print("\n原始关系类型:")
        for rel in sorted(df['predicate'].unique()):
            print(f"  - {rel}")
        
        # 规范化关系
        normalized_df = self._normalize_relations(df)
        
        # 显示规范化后的关系类型
        print(f"\n规范化后关系类型数量: {len(normalized_df['predicate'].unique())}")
        print("规范化后关系类型:")
        for rel in sorted(normalized_df['predicate'].unique()):
            print(f"  - {rel}")
        
        # 保存结果
        if output_file:
            normalized_df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"\n规范化后的知识图谱已保存到: {output_file}")
        
        return normalized_df
    
    def _normalize_relations(self, df: pd.DataFrame) -> pd.DataFrame:
        """规范化关系类型"""
        # 创建副本避免修改原始数据
        normalized_df = df.copy()
        
        # 记录原始关系
        original_relations = set(df['predicate'].unique())
        
        # 规范化关系类型
        normalized_df['predicate'] = normalized_df['predicate'].map(
            lambda x: self.relation_mapping.get(x, x) if pd.notna(x) else x
        )
        
        # 记录规范化统计
        normalized_relations = set(normalized_df['predicate'].unique())
        changed_count = len(original_relations - normalized_relations)
        
        print(f"\n关系规范化统计:")
        print(f"  - 修改的关系类型数量: {changed_count}")
        print(f"  - 规范化前关系数量: {len(original_relations)}")
        print(f"  - 规范化后关系数量: {len(normalized_relations)}")
        
        return normalized_df
    
    def generate_relation_report(self, df: pd.DataFrame) -> str:
        """生成关系规范化报告"""
        relations = df['predicate'].value_counts()
        
        report = f"""
# 关系规范化报告

## 关系类型统计
- 总关系类型数量: {len(relations)}
- 总三元组数量: {len(df)}

## 关系类型分布
"""
        
        for relation, count in relations.items():
            report += f"- {relation}: {count} 条\n"
        
        return report

def main():
    """主函数"""
    normalizer = RelationNormalizer()
    
    # 规范化增强后的知识图谱
    try:
        normalized_kg = normalizer.normalize_kg(
            "enhanced_knowledge_graph.csv",
            "normalized_knowledge_graph.csv"
        )
        
        # 生成报告
        report = normalizer.generate_relation_report(normalized_kg)
        print("\n" + report)
        
        # 保存报告
        with open("normalization_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("\n规范化报告已保存到: normalization_report.md")
        
    except FileNotFoundError:
        print("错误: 未找到 enhanced_knowledge_graph.csv 文件")
        print("请先运行知识图谱增强程序")
    except Exception as e:
        print(f"规范化失败: {e}")

if __name__ == "__main__":
    main()
