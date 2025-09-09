#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关系类型分析工具
分析知识图谱中的关系类型分布，识别冗余和优化机会
"""

import pandas as pd
import numpy as np
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import json

class RelationAnalyzer:
    """关系类型分析器"""
    
    def __init__(self, kg_file: str):
        """
        初始化分析器
        
        Args:
            kg_file: 知识图谱CSV文件路径
        """
        self.kg_file = kg_file
        self.kg_data = None
        self.load_knowledge_graph()
    
    def load_knowledge_graph(self):
        """加载知识图谱数据"""
        try:
            self.kg_data = pd.read_csv(self.kg_file)
            print(f"成功加载知识图谱，包含 {len(self.kg_data)} 条三元组")
        except Exception as e:
            print(f"加载知识图谱失败: {e}")
            raise
    
    def analyze_relations(self) -> Dict:
        """分析关系类型"""
        if self.kg_data is None:
            return {}
        
        # 统计关系类型
        relation_counts = self.kg_data['predicate'].value_counts()
        
        # 分析关系类型分布
        analysis = {
            "total_relations": len(relation_counts),
            "total_triples": len(self.kg_data),
            "relation_distribution": relation_counts.to_dict(),
            "high_frequency_relations": relation_counts[relation_counts >= 10].to_dict(),
            "medium_frequency_relations": relation_counts[(relation_counts >= 3) & (relation_counts < 10)].to_dict(),
            "low_frequency_relations": relation_counts[relation_counts < 3].to_dict(),
            "single_use_relations": relation_counts[relation_counts == 1].to_dict()
        }
        
        return analysis
    
    def identify_redundant_relations(self) -> Dict:
        """识别冗余关系"""
        if self.kg_data is None:
            return {}
        
        # 分析关系语义相似性
        semantic_groups = {
            "包含关系": ['contains', 'includes', 'has_part', 'consists_of'],
            "定义关系": ['is_defined_as', 'means', 'refers_to', 'denotes'],
            "属性关系": ['has_property', 'has_attribute', 'has_feature', 'has_characteristic'],
            "类型关系": ['is_a', 'is_type_of', 'belongs_to', 'is_instance_of'],
            "相关关系": ['related_to', 'associated_with', 'connected_to', 'linked_to'],
            "影响关系": ['affects', 'influences', 'impacts', 'affects'],
            "应用关系": ['applies_to', 'used_in', 'applied_in', 'utilized_in'],
            "转换关系": ['transforms_to', 'converts_to', 'changes_to', 'becomes'],
            "条件关系": ['requires', 'needs', 'depends_on', 'conditional_on'],
            "公式关系": ['has_formula', 'expressed_as', 'calculated_by', 'formula_is']
        }
        
        # 查找语义相似的关系
        redundant_groups = {}
        for group_name, similar_relations in semantic_groups.items():
            found_relations = []
            for rel in similar_relations:
                if rel in self.kg_data['predicate'].values:
                    count = len(self.kg_data[self.kg_data['predicate'] == rel])
                    found_relations.append((rel, count))
            
            if len(found_relations) > 1:
                redundant_groups[group_name] = found_relations
        
        return redundant_groups
    
    def suggest_relation_consolidation(self) -> Dict:
        """建议关系类型整合"""
        if self.kg_data is None:
            return {}
        
        # 分析当前关系使用情况
        relation_counts = self.kg_data['predicate'].value_counts()
        
        # 建议整合的关系类型
        consolidation_suggestions = {
            "高频关系（保留）": {
                "contains": "包含关系，使用频率高，保留",
                "is_defined_as": "定义关系，语义明确，保留",
                "has_property": "属性关系，使用广泛，保留",
                "has_formula": "公式关系，专业性强，保留",
                "has_condition": "条件关系，逻辑清晰，保留"
            },
            "中频关系（评估）": {
                "is_equivalent_to": "等价关系，语义明确",
                "transforms_to": "转换关系，逻辑清晰",
                "belongs_to": "归属关系，层次结构",
                "related_to": "相关关系，连接性强"
            },
            "低频关系（考虑整合）": {
                "can_be": "可整合为 has_capability",
                "may_be": "可整合为 has_potential",
                "could_be": "可整合为 has_possibility",
                "might_be": "可整合为 has_possibility"
            },
            "单次使用关系（建议整合）": {
                "single_use_relations": "建议整合到相近语义的关系中"
            }
        }
        
        return consolidation_suggestions
    
    def create_optimized_relation_schema(self) -> Dict:
        """创建优化的关系模式"""
        # 核心关系类型（建议保留）
        core_relations = {
            "structural": {
                "contains": "包含关系",
                "is_part_of": "组成部分关系",
                "belongs_to": "归属关系"
            },
            "semantic": {
                "is_defined_as": "定义关系",
                "means": "含义关系",
                "refers_to": "指代关系"
            },
            "properties": {
                "has_property": "属性关系",
                "has_feature": "特征关系",
                "has_characteristic": "特性关系"
            },
            "logical": {
                "implies": "蕴含关系",
                "requires": "需要关系",
                "depends_on": "依赖关系"
            },
            "mathematical": {
                "has_formula": "公式关系",
                "calculated_by": "计算关系",
                "expressed_as": "表达关系"
            },
            "application": {
                "applies_to": "应用关系",
                "used_in": "使用关系",
                "relevant_to": "相关关系"
            }
        }
        
        return core_relations
    
    def generate_optimization_report(self) -> str:
        """生成优化报告"""
        # 分析当前关系
        analysis = self.analyze_relations()
        redundant = self.identify_redundant_relations()
        suggestions = self.suggest_relation_consolidation()
        optimized_schema = self.create_optimized_relation_schema()
        
        report = f"""
# 知识图谱关系类型优化报告

## 当前状况分析

### 关系类型统计
- 总关系类型数量: {analysis['total_relations']}
- 总三元组数量: {analysis['total_triples']}
- 平均每种关系使用次数: {analysis['total_triples'] / analysis['total_relations']:.2f}

### 关系使用频率分布
- 高频关系 (≥10次): {len(analysis['high_frequency_relations'])} 种
- 中频关系 (3-9次): {len(analysis['medium_frequency_relations'])} 种  
- 低频关系 (1-2次): {len(analysis['low_frequency_relations'])} 种
- 单次使用关系: {len(analysis['single_use_relations'])} 种

## 冗余关系识别

### 语义相似关系组
"""
        
        for group_name, relations in redundant.items():
            report += f"\n**{group_name}**:\n"
            for rel, count in relations:
                report += f"- {rel}: {count} 次\n"
        
        report += f"""

## 优化建议

### 高频关系（建议保留）
"""
        
        for rel, count in analysis['high_frequency_relations'].items():
            report += f"- {rel}: {count} 次\n"
        
        report += f"""

### 中频关系（建议评估）
"""
        
        for rel, count in analysis['medium_frequency_relations'].items():
            report += f"- {rel}: {count} 次\n"
        
        report += f"""

### 低频关系（建议整合）
"""
        
        for rel, count in analysis['low_frequency_relations'].items():
            report += f"- {rel}: {count} 次\n"
        
        report += f"""

## 优化后的关系模式

### 建议保留的核心关系类型
"""
        
        total_core_relations = 0
        for category, relations in optimized_schema.items():
            report += f"\n**{category}**:\n"
            for rel, desc in relations.items():
                report += f"- {rel}: {desc}\n"
                total_core_relations += 1
        
        report += f"""

## 优化效果预估

- 当前关系类型数量: {analysis['total_relations']}
- 优化后关系类型数量: {total_core_relations}
- 预计减少: {analysis['total_relations'] - total_core_relations} 种关系类型
- 减少比例: {((analysis['total_relations'] - total_core_relations) / analysis['total_relations'] * 100):.1f}%

## 实施建议

1. **第一阶段**: 保留高频关系（≥10次使用）
2. **第二阶段**: 评估中频关系（3-9次使用）
3. **第三阶段**: 整合低频关系（1-2次使用）
4. **第四阶段**: 建立关系类型标准规范

## 注意事项

- 关系整合需要保持语义一致性
- 建议分阶段实施，避免一次性大幅修改
- 需要领域专家验证整合的合理性
- 建立关系类型使用指南和规范
        """
        
        return report
    
    def export_analysis_data(self, output_file: str = "relation_analysis.json"):
        """导出分析数据"""
        analysis = self.analyze_relations()
        redundant = self.identify_redundant_relations()
        suggestions = self.suggest_relation_consolidation()
        optimized_schema = self.create_optimized_relation_schema()
        
        export_data = {
            "current_analysis": analysis,
            "redundant_relations": redundant,
            "consolidation_suggestions": suggestions,
            "optimized_schema": optimized_schema
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"分析数据已导出到: {output_file}")

def main():
    """主函数"""
    try:
        # 创建分析器
        analyzer = RelationAnalyzer("normalized_knowledge_graph.csv")
        
        print("=== 关系类型分析工具 ===")
        
        # 分析关系类型
        print("1. 分析关系类型分布...")
        analysis = analyzer.analyze_relations()
        
        print(f"总关系类型数量: {analysis['total_relations']}")
        print(f"高频关系数量: {len(analysis['high_frequency_relations'])}")
        print(f"中频关系数量: {len(analysis['medium_frequency_relations'])}")
        print(f"低频关系数量: {len(analysis['low_frequency_relations'])}")
        print(f"单次使用关系数量: {len(analysis['single_use_relations'])}")
        
        # 识别冗余关系
        print("\n2. 识别冗余关系...")
        redundant = analyzer.identify_redundant_relations()
        print(f"发现 {len(redundant)} 组语义相似的关系")
        
        # 生成优化报告
        print("\n3. 生成优化报告...")
        report = analyzer.generate_optimization_report()
        
        # 保存报告
        with open("relation_optimization_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("优化报告已保存到: relation_optimization_report.md")
        
        # 导出分析数据
        print("\n4. 导出分析数据...")
        analyzer.export_analysis_data()
        
        print("\n=== 分析完成 ===")
        
    except Exception as e:
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
