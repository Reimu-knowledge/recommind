#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关系类型优化工具
整合冗余关系类型，简化知识图谱结构
"""

import pandas as pd
import json
from typing import Dict, List, Tuple

class RelationOptimizer:
    """关系类型优化器"""
    
    def __init__(self, kg_file: str):
        """
        初始化优化器
        
        Args:
            kg_file: 知识图谱CSV文件路径
        """
        self.kg_file = kg_file
        self.kg_data = None
        self.load_knowledge_graph()
        
        # 关系整合映射
        self.relation_consolidation = {
            # 相关关系整合
            'associated_with': 'related_to',
            'connected_to': 'related_to',
            'linked_to': 'related_to',
            'relates_to': 'related_to',
            
            # 影响关系整合
            'impacts': 'affects',
            'influences': 'affects',
            
            # 应用关系整合
            'used_in': 'applies_to',
            'applied_in': 'applies_to',
            'utilized_in': 'applies_to',
            'application': 'applies_to',
            'application_in': 'applies_to',
            'application_relation': 'applies_to',
            
            # 转换关系整合
            'converts_to': 'transforms_to',
            'changes_to': 'transforms_to',
            'becomes': 'transforms_to',
            'can_be_transformed_into': 'transforms_to',
            'can_convert_to': 'transforms_to',
            'can_transform_to_tree_subgraph': 'transforms_to',
            
            # 属性关系整合
            'has_attribute': 'has_property',
            'has_feature': 'has_property',
            'has_characteristic': 'has_property',
            'satisfies_property': 'has_property',
            'preserves_property': 'has_property',
            
            # 类型关系整合
            'is_type_of': 'is_a',
            'is_instance_of': 'is_a',
            'belongs_to': 'is_a',
            
            # 定义关系整合
            'means': 'is_defined_as',
            'refers_to': 'is_defined_as',
            'denotes': 'is_defined_as',
            
            # 公式关系整合
            'expressed_as': 'has_formula',
            'calculated_by': 'has_formula',
            'formula_is': 'has_formula',
            
            # 条件关系整合
            'needs': 'has_condition',
            'depends_on': 'has_condition',
            'conditional_on': 'has_condition',
            'implies_condition': 'has_condition',
            'requires': 'has_condition',
            
            # 包含关系整合
            'includes': 'contains',
            'has_part': 'contains',
            'consists_of': 'contains',
            'contains_spanning_tree': 'contains',
            'contains_perfect_matching_under_certain_conditions': 'contains',
            
            # 等价关系整合
            'is_equivalent_to': 'is_equivalent_to',  # 保持不变
            
            # 能力关系整合
            'can_be': 'has_capability',
            'may_be': 'has_potential',
            'could_be': 'has_possibility',
            'might_be': 'has_possibility',
            'can_model': 'has_capability',
            'can_represent': 'has_capability',
            'can_degenerate_to': 'has_capability',
            'can_have': 'has_capability',
            'may_have': 'has_potential',
            'may_be_tree_structure': 'has_potential',
            'may_be_planar': 'has_potential',
            
            # 支持关系整合
            'supports': 'supports',  # 保持不变
            'allows': 'supports',
            'is_essential_for': 'supports',
            'is_necessary_for': 'supports',
            
            # 算法关系整合
            'uses_algorithm': 'uses_algorithm',  # 保持不变
            
            # 隐含关系整合
            'implies': 'implies',  # 保持不变
            'implicit_connection': 'implies',
            
            # 特殊图论关系整合
            'no_triangle_structure': 'has_property',
            'vertex_cover_equals_max_matching': 'has_property',
            'matching_problem_has_special_properties': 'has_property',
            'suitable_for_bipartite_matching_algorithm': 'has_property',
            'can_be_bicolored': 'has_property',
            'is_bipartite': 'has_property',
            'has_chromatic_number_2': 'has_property',
            'has_spanning_forest_structure': 'has_property',
            'has_max_edges': 'has_property',
            'related_to_connectivity': 'related_to',
            'related_to_max_degree': 'related_to',
            'affected_by_max_degree': 'affected_by',
            'constrained_by': 'constrained_by',  # 保持不变
            'involves_coloring': 'involves',
            'involves': 'involves',  # 保持不变
        }
    
    def load_knowledge_graph(self):
        """加载知识图谱数据"""
        try:
            self.kg_data = pd.read_csv(self.kg_file)
            print(f"成功加载知识图谱，包含 {len(self.kg_data)} 条三元组")
        except Exception as e:
            print(f"加载知识图谱失败: {e}")
            raise
    
    def optimize_relations(self) -> pd.DataFrame:
        """优化关系类型"""
        if self.kg_data is None:
            return pd.DataFrame()
        
        # 创建副本避免修改原始数据
        optimized_df = self.kg_data.copy()
        
        # 记录原始关系统计
        original_relations = set(optimized_df['predicate'].unique())
        print(f"优化前关系类型数量: {len(original_relations)}")
        
        # 应用关系整合映射
        optimized_df['predicate'] = optimized_df['predicate'].map(
            lambda x: self.relation_consolidation.get(x, x) if pd.notna(x) else x
        )
        
        # 记录优化后关系统计
        optimized_relations = set(optimized_df['predicate'].unique())
        print(f"优化后关系类型数量: {len(optimized_relations)}")
        print(f"减少关系类型数量: {len(original_relations) - len(optimized_relations)}")
        
        return optimized_df
    
    def generate_optimization_summary(self, original_df: pd.DataFrame, optimized_df: pd.DataFrame) -> str:
        """生成优化总结"""
        original_relations = set(original_df['predicate'].unique())
        optimized_relations = set(optimized_df['predicate'].unique())
        
        # 统计关系使用频率
        original_counts = original_df['predicate'].value_counts()
        optimized_counts = optimized_df['predicate'].value_counts()
        
        summary = f"""
# 关系类型优化总结

## 优化效果
- 原始关系类型数量: {len(original_relations)}
- 优化后关系类型数量: {len(optimized_relations)}
- 减少关系类型数量: {len(original_relations) - len(optimized_relations)}
- 减少比例: {((len(original_relations) - len(optimized_relations)) / len(original_relations) * 100):.1f}%

## 主要整合关系

### 高频关系（保持不变）
"""
        
        # 显示高频关系
        high_freq_relations = optimized_counts[optimized_counts >= 10]
        for rel, count in high_freq_relations.items():
            summary += f"- {rel}: {count} 次\n"
        
        summary += f"""

### 整合后的关系类型
"""
        
        # 显示所有优化后的关系类型
        for rel, count in optimized_counts.items():
            summary += f"- {rel}: {count} 次\n"
        
        summary += f"""

## 整合规则说明

### 相关关系 → related_to
- associated_with, connected_to, linked_to, relates_to

### 影响关系 → affects  
- impacts, influences

### 应用关系 → applies_to
- used_in, applied_in, utilized_in, application, application_in

### 转换关系 → transforms_to
- converts_to, changes_to, becomes, can_be_transformed_into

### 属性关系 → has_property
- has_attribute, has_feature, has_characteristic, satisfies_property

### 类型关系 → is_a
- is_type_of, is_instance_of, belongs_to

### 能力关系 → has_capability/has_potential
- can_be, may_be, could_be, might_be, can_model

## 优化建议

1. **保持核心关系**: 高频关系（≥10次使用）保持不变
2. **整合相似关系**: 语义相似的关系整合为统一类型
3. **简化特殊关系**: 过于具体的关系整合为通用类型
4. **建立标准规范**: 制定关系类型使用指南

## 注意事项

- 关系整合保持了语义一致性
- 建议分阶段实施，避免一次性大幅修改
- 需要领域专家验证整合的合理性
- 建立关系类型使用指南和规范
        """
        
        return summary
    
    def export_optimized_kg(self, optimized_df: pd.DataFrame, output_file: str = "optimized_knowledge_graph.csv"):
        """导出优化后的知识图谱"""
        optimized_df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"优化后的知识图谱已保存到: {output_file}")
    
    def export_optimization_report(self, summary: str, output_file: str = "optimization_summary.md"):
        """导出优化报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"优化报告已保存到: {output_file}")

def main():
    """主函数"""
    try:
        # 创建优化器
        optimizer = RelationOptimizer("normalized_knowledge_graph.csv")
        
        print("=== 关系类型优化工具 ===")
        
        # 优化关系类型
        print("1. 开始优化关系类型...")
        optimized_kg = optimizer.optimize_relations()
        
        # 生成优化总结
        print("2. 生成优化总结...")
        summary = optimizer.generate_optimization_summary(optimizer.kg_data, optimized_kg)
        
        # 保存优化后的知识图谱
        print("3. 保存优化结果...")
        optimizer.export_optimized_kg(optimized_kg)
        
        # 保存优化报告
        print("4. 保存优化报告...")
        optimizer.export_optimization_report(summary)
        
        print("\n=== 关系类型优化完成 ===")
        
    except Exception as e:
        print(f"优化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
