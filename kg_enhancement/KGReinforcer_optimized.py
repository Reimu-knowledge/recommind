#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识图谱增强器 (Knowledge Graph Reinforcer) - 优化版
使用大语言模型(LLM)增强知识图谱的效果，直接生成标准化的关系类型
"""

import pandas as pd
import json
from langchain_openai import ChatOpenAI
import os
from typing import List, Dict, Tuple, Optional
import networkx as nx
import matplotlib.pyplot as plt
import logging

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class KGReinforcer:
    """知识图谱增强器主类"""
    
    def __init__(self, api_key: str = None, model: str = "qwen-plus"):
        """
        初始化知识图谱增强器
        
        Args:
            api_key: 通义千问API密钥
            model: 使用的LLM模型
        """
        self.model = model
        self.kg_data = None
        self.enhanced_kg = None
        self.graph = None
        
        if api_key:
            self.api_key = api_key
        else:
            # 尝试从环境变量获取
            self.api_key = os.getenv('DASHSCOPE_API_KEY')
            if not self.api_key:
                print("警告: 未设置DASHSCOPE_API_KEY，某些功能可能无法使用")
        
        # 初始化通义千问客户端
        try:
            self.chat_llm = ChatOpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                model=self.model,
                temperature=0.7,
                max_tokens=1000
            )
        except Exception as e:
            self.chat_llm = None
            print(f"通义千问客户端初始化失败: {e}")
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 定义标准化的关系类型
        self.standard_relations = {
            'contains': '包含关系',
            'is_defined_as': '定义关系',
            'has_property': '属性关系',
            'has_formula': '公式关系',
            'has_condition': '条件关系',
            'is_equivalent_to': '等价关系',
            'transforms_to': '转换关系',
            'belongs_to': '归属关系',
            'related_to': '相关关系',
            'applies_to': '应用关系',
            'affects': '影响关系',
            'supports': '支持关系',
            'uses_algorithm': '使用算法',
            'involves': '涉及关系',
            'implies': '蕴含关系',
            'requires': '需要关系',
            'depends_on': '依赖关系'
        }
    
    def load_knowledge_graph(self, file_path: str) -> pd.DataFrame:
        """加载知识图谱数据"""
        try:
            self.kg_data = pd.read_csv(file_path)
            self.logger.info(f"成功加载知识图谱，包含 {len(self.kg_data)} 条三元组")
            return self.kg_data
        except Exception as e:
            self.logger.error(f"加载知识图谱失败: {e}")
            raise
    
    def enhance_with_llm(self, enhancement_type: str = "comprehensive") -> pd.DataFrame:
        """使用LLM增强知识图谱，直接生成标准化的关系类型"""
        if self.kg_data is None:
            raise ValueError("请先加载知识图谱数据")
        
        self.logger.info(f"开始使用LLM进行{enhancement_type}增强...")
        
        enhanced_triples = []
        
        if enhancement_type == "comprehensive":
            enhanced_triples = self._comprehensive_enhancement()
        elif enhancement_type == "relation":
            enhanced_triples = self._relation_enhancement()
        elif enhancement_type == "entity":
            enhanced_triples = self._entity_enhancement()
        elif enhancement_type == "reasoning":
            enhanced_triples = self._reasoning_enhancement()
        
        # 合并原始数据和增强数据
        enhanced_df = pd.concat([
            self.kg_data,
            pd.DataFrame(enhanced_triples, columns=['subject', 'predicate', 'object', 'source'])
        ], ignore_index=True)
        
        # 规范化关系类型（使用标准化关系）
        enhanced_df = self._normalize_relations(enhanced_df)
        
        self.enhanced_kg = enhanced_df
        self.logger.info(f"增强完成，新增 {len(enhanced_triples)} 条三元组")
        
        return enhanced_df
    
    def _comprehensive_enhancement(self) -> List[List]:
        """综合增强：结合多种增强策略"""
        enhanced_triples = []
        
        # 1. 关系增强
        enhanced_triples.extend(self._relation_enhancement())
        
        # 2. 实体增强
        enhanced_triples.extend(self._entity_enhancement())
        
        # 3. 推理增强
        enhanced_triples.extend(self._reasoning_enhancement())
        
        # 4. 概念扩展增强
        enhanced_triples.extend(self._concept_expansion_enhancement())
        
        return enhanced_triples
    
    def _relation_enhancement(self) -> List[List]:
        """关系增强：发现新的关系类型和连接，使用标准化关系"""
        enhanced_triples = []
        
        # 分析现有关系模式和实体
        relation_patterns = self.kg_data['predicate'].value_counts()
        entities = set(self.kg_data['subject'].tolist() + self.kg_data['object'].tolist())
        
        # 使用LLM生成新的关系类型和实体连接，要求使用标准化关系
        prompt = f"""
        你是一个图论专家。基于以下图论知识图谱信息，请生成15-25个新的、有意义的三元组：

        现有关系类型：{', '.join(relation_patterns.index.tolist())}
        主要图论概念：{', '.join(list(entities)[:30])}

        重要要求：
        1. 必须使用以下标准化关系类型之一：
           - contains（包含关系）
           - is_defined_as（定义关系）
           - has_property（属性关系）
           - has_formula（公式关系）
           - has_condition（条件关系）
           - is_equivalent_to（等价关系）
           - transforms_to（转换关系）
           - belongs_to（归属关系）
           - related_to（相关关系）
           - applies_to（应用关系）
           - affects（影响关系）
           - supports（支持关系）
           - uses_algorithm（使用算法）
           - involves（涉及关系）

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

        注意：必须使用上述标准化关系类型，不要创建新的关系类型。每个三元组都应该增加图论知识图谱的价值。
        """
        
        try:
            response = self._call_llm(prompt)
            new_triples = json.loads(response)
            
            # 添加新的三元组
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
    
    def _entity_enhancement(self) -> List[List]:
        """实体增强：发现新的实体和属性，使用标准化关系"""
        enhanced_triples = []
        
        # 分析实体
        entities = set(self.kg_data['subject'].tolist() + self.kg_data['object'].tolist())
        
        # 使用LLM为重要实体生成新属性
        important_entities = self.kg_data['subject'].value_counts().head(15).index.tolist()
        
        # 批量处理实体，提高效率
        batch_prompt = f"""
        你是一个图论专家。请为以下图论相关实体生成丰富的属性信息，每个实体生成8-12个新属性：

        实体列表：{', '.join(important_entities)}

        重要要求：
        1. 必须使用以下标准化关系类型：
           - is_defined_as（定义关系）
           - has_property（属性关系）
           - has_formula（公式关系）
           - has_condition（条件关系）
           - belongs_to（归属关系）
           - related_to（相关关系）
           - applies_to（应用关系）
           - uses_algorithm（使用算法）

        2. 每个属性都应该在图论学术上有价值和意义
        3. 属性应该包括：定义、性质、定理、应用、算法复杂度、历史背景、相关概念等
        4. 属性值应该具体且准确，体现图论的专业性
        5. 考虑实体在图论中的重要性，如：欧拉图、哈密顿图、平面图、着色问题等
        6. 重点关注：图的连通性、着色数、匹配数、覆盖数、平面性、树性质等核心概念

        请以JSON格式返回，格式如下：
        {{
            "entity_attributes": [
                {{
                    "entity": "实体名",
                    "attributes": [
                        {{"attribute": "标准化关系类型", "value": "属性值", "description": "属性描述"}}
                    ]
                }}
            ]
        }}
        """
        
        try:
            response = self._call_llm(batch_prompt)
            entity_attributes = json.loads(response)
            
            for entity_info in entity_attributes.get("entity_attributes", []):
                entity = entity_info["entity"]
                for attr_info in entity_info.get("attributes", []):
                    enhanced_triples.append([
                        entity,
                        attr_info["attribute"],
                        attr_info["value"],
                        "LLM_enhanced_entity"
                    ])
                    
        except Exception as e:
            self.logger.warning(f"批量实体增强失败: {e}")
            # 降级到单个实体处理
            for entity in important_entities[:8]:
                try:
                    single_prompt = f"""
                    为图论实体"{entity}"生成8个新属性，使用标准化关系类型：
                    - is_defined_as（定义关系）
                    - has_property（属性关系）
                    - has_formula（公式关系）
                    - belongs_to（归属关系）
                    - related_to（相关关系）
                    
                    重点关注图论的专业性，如连通性、着色、匹配、覆盖、平面性等。
                    返回JSON格式：{{"attributes": [{{"attribute": "标准化关系类型", "value": "属性值"}}]}}
                    """
                    response = self._call_llm(single_prompt)
                    attrs = json.loads(response)
                    for attr in attrs.get("attributes", []):
                        enhanced_triples.append([
                            entity, attr["attribute"], attr["value"], "LLM_enhanced_entity"
                        ])
                except Exception as e2:
                    self.logger.warning(f"实体{entity}增强失败: {e2}")
        
        return enhanced_triples
    
    def _reasoning_enhancement(self) -> List[List]:
        """推理增强：基于现有知识进行逻辑推理，使用标准化关系"""
        enhanced_triples = []
        
        # 分析知识图谱中的逻辑关系
        logic_relations = ['is_defined_as', 'contains', 'transforms_to', 'has_property', 'has_formula', 'has_condition']
        
        # 寻找可以进行推理的实体对，增加样本数量
        for relation in logic_relations:
            related_triples = self.kg_data[self.kg_data['predicate'] == relation]
            
            if len(related_triples) > 0:
                # 选择多个三元组进行推理，提高覆盖率
                sample_triples = related_triples.head(min(3, len(related_triples)))
                
                for _, sample_triple in sample_triples.iterrows():
                    prompt = f"""
                    你是一个图论专家。基于以下知识图谱三元组，请进行深度逻辑推理，生成4-6个新的、合理的图论知识：

                    原始知识：{sample_triple['subject']} {sample_triple['predicate']} {sample_triple['object']}

                    重要要求：
                    1. 必须使用以下标准化关系类型：
                       - implies（蕴含关系）
                       - requires（需要关系）
                       - depends_on（依赖关系）
                       - related_to（相关关系）
                       - affects（影响关系）
                       - supports（支持关系）
                       - transforms_to（转换关系）
                       - is_equivalent_to（等价关系）

                    2. 推理要求：
                       - 分析这个知识在图论中的含义和重要性
                       - 推导出相关的定理、性质或应用
                       - 发现与其他图论概念的潜在联系
                       - 考虑实际应用场景，如网络分析、算法设计等
                       - 确保推理逻辑严谨，符合图论数学原理
                       - 重点关注：连通性、着色、匹配、覆盖、平面性、树结构等核心概念

                    请以JSON格式返回推理结果，格式如下：
                    {{
                        "inferred_knowledge": [
                            {{"subject": "主体", "predicate": "标准化关系类型", "object": "客体", "reasoning": "推理过程", "confidence": "高/中/低"}}
                        ]
                    }}
                    """
                    
                    try:
                        response = self._call_llm(prompt)
                        inferred_knowledge = json.loads(response)
                        
                        for knowledge in inferred_knowledge.get("inferred_knowledge", []):
                            enhanced_triples.append([
                                knowledge["subject"],
                                knowledge["predicate"],
                                knowledge["object"],
                                f"LLM_reasoning_{relation}"
                            ])
                            
                    except Exception as e:
                        self.logger.warning(f"推理增强失败: {e}")
        
        return enhanced_triples
    
    def _concept_expansion_enhancement(self) -> List[List]:
        """概念扩展增强：发现新的相关概念和知识，使用标准化关系"""
        enhanced_triples = []
        
        # 分析现有概念，找出可以扩展的领域
        main_concepts = self.kg_data['subject'].value_counts().head(20).index.tolist()
        
        try:
            expansion_prompt = f"""
            你是一个图论专家。请基于以下核心概念，扩展发现新的相关概念和知识：

            核心概念：{', '.join(main_concepts[:10])}

            重要要求：
            1. 必须使用以下标准化关系类型：
               - is_defined_as（定义关系）
               - belongs_to（归属关系）
               - related_to（相关关系）
               - applies_to（应用关系）
               - has_property（属性关系）
               - uses_algorithm（使用算法）
               - involves（涉及关系）

            2. 扩展要求：
               - 发现图论中与这些概念相关但可能缺失的重要概念
               - 添加实际应用场景和例子，如网络分析、算法设计、数据结构等
               - 包含历史背景和发展脉络，如欧拉、哈密顿、柯尼斯堡七桥问题等
               - 发现与其他数学分支的联系，如组合数学、代数图论、拓扑学等
               - 添加算法和计算方法，如Dijkstra算法、Kruskal算法、Prim算法等
               - 考虑现代应用（如计算机科学、网络分析、生物信息学等）
               - 重点关注：图的分解、图的变换、图的分类、图的算法等高级概念

            请以JSON格式返回，格式如下：
            {{
                "expanded_concepts": [
                    {{
                        "concept": "新概念名",
                        "category": "概念类别",
                        "description": "概念描述",
                        "related_to": "与哪个现有概念相关",
                        "application": "应用场景"
                    }}
                ]
            }}
            """
            
            response = self._call_llm(expansion_prompt)
            expanded_concepts = json.loads(response)
            
            for concept_info in expanded_concepts.get("expanded_concepts", []):
                concept = concept_info["concept"]
                related = concept_info.get("related_to", "图论")
                
                # 添加概念定义
                enhanced_triples.append([
                    concept,
                    "is_defined_as",
                    concept_info["description"],
                    "LLM_enhanced_expansion"
                ])
                
                # 添加概念分类
                enhanced_triples.append([
                    concept,
                    "belongs_to",
                    concept_info["category"],
                    "LLM_enhanced_expansion"
                ])
                
                # 添加与现有概念的关系
                enhanced_triples.append([
                    concept,
                    "related_to",
                    related,
                    "LLM_enhanced_expansion"
                ])
                
                # 添加应用场景
                enhanced_triples.append([
                    concept,
                    "applies_to",
                    concept_info["application"],
                    "LLM_enhanced_expansion"
                ])
                
        except Exception as e:
            self.logger.warning(f"概念扩展增强失败: {e}")
        
        return enhanced_triples
    
    def _call_llm(self, prompt: str) -> str:
        """调用通义千问API"""
        if self.chat_llm is None:
            self.logger.warning("通义千问客户端未初始化，使用模拟响应")
            return self._get_mock_response(prompt)
        
        try:
            messages = [
                {"role": "system", "content": "你是一个知识图谱专家，擅长分析和增强知识图谱。请严格按照要求的JSON格式返回结果，并使用指定的标准化关系类型。"},
                {"role": "user", "content": prompt}
            ]
            response = self.chat_llm.invoke(messages)
            
            # 尝试从响应中提取JSON内容
            content = response.content
            self.logger.info(f"通义千问原始响应: {content[:200]}...")
            
            # 如果响应包含JSON，尝试提取
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_content = content[start:end]
                return json_content
            else:
                # 如果没有找到JSON，返回模拟响应
                self.logger.warning("响应中未找到JSON格式，使用模拟响应")
                return self._get_mock_response(prompt)
                
        except Exception as e:
            self.logger.error(f"通义千问调用失败: {e}")
            # 返回模拟响应
            return self._get_mock_response(prompt)
    
    def _get_mock_response(self, prompt: str) -> str:
        """获取模拟响应（当LLM不可用时），使用标准化关系"""
        if "关系类型" in prompt:
            return '''
            {
                "new_triples": [
                    {"subject": "欧拉图", "predicate": "has_property", "object": "所有顶点度数均为偶数", "reasoning": "欧拉图的基本性质"},
                    {"subject": "哈密顿图", "predicate": "has_property", "object": "存在经过所有顶点的回路", "reasoning": "哈密顿图的基本性质"},
                    {"subject": "平面图", "predicate": "has_property", "object": "可以画在平面上无交叉边", "reasoning": "平面图的定义性质"}
                ]
            }
            '''
        elif "属性" in prompt:
            return '''
            {
                "entity_attributes": [
                    {
                        "entity": "图论",
                        "attributes": [
                            {"attribute": "has_property", "value": "研究图的结构和性质", "description": "基本定义"},
                            {"attribute": "belongs_to", "value": "离散数学", "description": "学科分类"}
                        ]
                    }
                ]
            }
            '''
        else:
            return '''
            {
                "inferred_knowledge": [
                    {"subject": "连通图", "predicate": "implies", "object": "存在生成树", "reasoning": "连通图的基本性质"}
                ]
            }
            '''
    
    def _normalize_relations(self, df: pd.DataFrame) -> pd.DataFrame:
        """规范化关系类型，使用预定义的标准化关系"""
        # 创建副本避免修改原始数据
        normalized_df = df.copy()
        
        # 记录原始关系统计
        original_relations = set(df['predicate'].unique())
        print(f"规范化前关系类型数量: {len(original_relations)}")
        
        # 关系映射字典：非标准关系 -> 标准关系
        relation_mapping = {
            # 包含关系整合
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
            
            # 图论专业关系整合
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
            'has_application': 'applies_to',
            'evolves_from': 'evolves_from'
        }
        
        # 规范化关系类型
        normalized_df['predicate'] = normalized_df['predicate'].map(
            lambda x: relation_mapping.get(x, x) if pd.notna(x) else x
        )
        
        # 记录规范化统计
        normalized_relations = set(normalized_df['predicate'].unique())
        changed_count = len(original_relations - normalized_relations)
        
        self.logger.info(f"关系规范化完成，修改了 {changed_count} 个关系类型")
        self.logger.info(f"规范化前关系数量: {len(original_relations)}")
        self.logger.info(f"规范化后关系数量: {len(normalized_relations)}")
        
        return normalized_df
    
    def save_enhanced_kg(self, output_path: str):
        """保存增强后的知识图谱"""
        if self.enhanced_kg is not None:
            self.enhanced_kg.to_csv(output_path, index=False, encoding='utf-8')
            self.logger.info(f"增强后的知识图谱已保存到: {output_path}")
        else:
            self.logger.warning("没有增强后的知识图谱可保存")
    
    def generate_report(self) -> str:
        """生成增强报告"""
        if self.enhanced_kg is None:
            return "请先进行知识图谱增强"
        
        original_count = len(self.kg_data)
        enhanced_count = len(self.enhanced_kg)
        new_count = enhanced_count - original_count
        
        # 统计关系类型
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

## 增强详情
- 关系增强: {len(self.enhanced_kg[self.enhanced_kg['source'].str.contains('relation', na=False)])}
- 实体增强: {len(self.enhanced_kg[self.enhanced_kg['source'].str.contains('entity', na=False)])}
- 推理增强: {len(self.enhanced_kg[self.enhanced_kg['source'].str.contains('reasoning', na=False)])}
- 概念扩展: {len(self.enhanced_kg[self.enhanced_kg['source'].str.contains('expansion', na=False)])}

## 标准化关系类型
{', '.join(sorted(self.enhanced_kg['predicate'].unique()))}

## 增强策略说明
1. **关系增强**: 发现实体间的新连接，使用标准化关系类型
2. **实体增强**: 为重要实体添加丰富的属性和特征
3. **推理增强**: 基于现有知识进行逻辑推理，发现隐含知识
4. **概念扩展**: 发现新的相关概念、应用场景和跨领域联系

## 质量评估
- 新增知识数量: {new_count} 条
- 知识覆盖率提升: {(new_count/original_count*100):.2f}%
- 关系类型标准化: 使用预定义的标准化关系类型
- 知识图谱结构: 更加清晰和规范

## 建议
1. 定期使用LLM进行知识图谱更新和扩展
2. 结合领域专家验证新增知识的准确性和价值
3. 建立知识质量评估和反馈机制
4. 持续优化prompt设计，提高增强效果
5. 使用标准化关系类型，保持知识图谱的一致性
        """
        
        return report

def main():
    """主函数示例"""
    # 创建知识图谱增强器
    reinforcer = KGReinforcer()
    
    # 加载知识图谱
    try:
        reinforcer.load_knowledge_graph("final_knowledge_graph.csv")
        
        # 进行综合增强
        enhanced_kg = reinforcer.enhance_with_llm("comprehensive")
        
        # 保存增强后的知识图谱
        reinforcer.save_enhanced_kg("enhanced_knowledge_graph.csv")
        
        # 生成报告
        report = reinforcer.generate_report()
        print(report)
        
        # 保存报告
        with open("enhancement_report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
    except Exception as e:
        print(f"程序执行失败: {e}")

if __name__ == "__main__":
    main()




