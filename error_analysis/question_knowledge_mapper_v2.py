#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图论选择题与知识图谱映射工具 V2
实现用户提出的方案：提取知识点，分批询问大模型进行映射
"""

import pandas as pd
import numpy as np
import json
import re
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Set
import time
import os
import logging
from langchain_openai import ChatOpenAI

class QuestionKnowledgeMapperV2:
    """题目-知识图谱映射器 V2"""
    
    def __init__(self, questions_file: str, kg_file: str, api_key: str = None, model: str = "qwen-plus"):
        """
        初始化映射器
        
        Args:
            questions_file: 题目CSV文件路径
            kg_file: 知识图谱CSV文件路径
            api_key: 通义千问API密钥
            model: 使用的LLM模型
        """
        self.questions_file = questions_file
        self.kg_file = kg_file
        self.questions_data = None
        self.kg_data = None
        self.knowledge_points = None
        self.mapping_results = None
        self.model = model
        
        # 设置API密钥
        if api_key:
            self.api_key = api_key
        else:
            # 尝试从环境变量获取
            self.api_key = os.getenv('DASHSCOPE_API_KEY')
            if not self.api_key:
                print("警告: 未设置DASHSCOPE_API_KEY，将使用模拟响应")
        
        # 初始化通义千问客户端
        try:
            self.chat_llm = ChatOpenAI(
                api_key=self.api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                model=self.model,
                temperature=0.3,  # 降低温度以获得更一致的结果
                max_tokens=2000
            )
            print("✓ 通义千问客户端初始化成功")
        except Exception as e:
            self.chat_llm = None
            print(f"通义千问客户端初始化失败: {e}")
            print("将使用模拟响应模式")
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 加载数据
        self.load_data()
    
    def load_data(self):
        """加载题目和知识图谱数据"""
        try:
            # 尝试不同的编码方式加载题目文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            for encoding in encodings:
                try:
                    self.questions_data = pd.read_csv(self.questions_file, encoding=encoding)
                    print(f"成功加载题目文件，使用编码: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if self.questions_data is None:
                raise ValueError("无法读取题目文件，请检查文件编码")
            
            # 加载知识图谱
            self.kg_data = pd.read_csv(self.kg_file)
            print(f"成功加载知识图谱，包含 {len(self.kg_data)} 条三元组")
            
            # 提取所有知识点
            self.extract_knowledge_points()
            
        except Exception as e:
            print(f"加载数据失败: {e}")
            raise
    
    def extract_knowledge_points(self):
        """从知识图谱中提取所有知识点（去重）"""
        # 提取所有唯一的概念（subject和object）
        subjects = set(self.kg_data['subject'].unique())
        objects = set(self.kg_data['object'].unique())
        all_concepts = subjects.union(objects)
        
        # 过滤掉一些不太重要的概念（如标点符号、数字等）
        filtered_concepts = []
        for concept in all_concepts:
            if isinstance(concept, str) and len(concept.strip()) > 0:
                # 过滤掉纯数字、单个字符等
                if not concept.isdigit() and len(concept) > 1:
                    filtered_concepts.append(concept)
        
        self.knowledge_points = sorted(filtered_concepts)
        print(f"提取到 {len(self.knowledge_points)} 个知识点")
    
    def batch_knowledge_points(self, batch_size: int = 10) -> List[List[str]]:
        """将知识点分批"""
        batches = []
        for i in range(0, len(self.knowledge_points), batch_size):
            batch = self.knowledge_points[i:i + batch_size]
            batches.append(batch)
        return batches
    
    def create_llm_prompt(self, question: Dict, knowledge_batch: List[str]) -> str:
        """创建询问大模型的提示词（单题版本）"""
        import random
        import time
        
        # 添加随机标识符打破模型记忆
        random_id = random.randint(1000, 9999)
        timestamp = int(time.time() * 1000) % 10000
        
        prompt = f"""
你是一个图论专家，具有深厚的图论理论基础和丰富的教学经验。请深入分析以下图论选择题，准确判断题目和选项对应了给定的知识点中的哪些。

【重要提醒】这是第{random_id}次独立分析，请忽略之前任何分析结果。你只能使用下面列出的知识点。

当前批次的知识点列表（你只能使用这些知识点，不能使用任何其他概念）：
{chr(10).join([f"{i+1}. {knowledge}" for i, knowledge in enumerate(knowledge_batch)])}

待分析的题目：
题目：{question['question']}
选项A：{question['option_a']}
选项B：{question['option_b']}
选项C：{question['option_c']}
选项D：{question['option_d']}

【关键约束】请逐项检查上述知识点列表，只有当题目或选项中明确包含某个知识点时，才返回该知识点。绝对不要使用列表外的任何概念。

请严格按照以下JSON格式返回结果：
{{
    "question_id": {question['id']},
    "question_concepts": ["知识点1", "知识点2"],
    "option_a_concepts": ["知识点3"],
    "option_b_concepts": ["知识点4", "知识点5"],
    "option_c_concepts": [],
    "option_d_concepts": ["知识点6"]
}}

关键要求：
1. 知识点名称必须完全来自给定的知识点列表，一个字都不能差
2. 如果题目或选项涉及的概念在知识点列表中不存在，必须返回空列表[]
3. 绝对不要创造新的知识点名称，不要使用"知识点1"、"知识点2"这样的占位符
4. 绝对不要使用同义词、近义词或重新表述
5. 知识点名称必须与列表中的完全一致，包括标点符号、空格、格式
6. 禁止将多个知识点合并或拆分，禁止创造复合概念
7. 禁止使用图论中的标准术语，除非它们完全匹配知识点列表中的名称

匹配规则：
1. 逐字对比题目/选项内容与知识点列表中的每个知识点
2. 只有当题目/选项中明确包含知识点名称时，才返回该知识点
3. 如果找不到完全匹配的知识点，返回空列表[]
4. 不要进行语义推理或概念扩展
5. 不要将"强连通"扩展为"强连通图"，不要将"连通"扩展为"连通图"

重要提醒：
- 你只能使用给定的知识点列表中的确切名称
- 即使你知道图论中的标准概念名称，如果它不在给定的列表中，也不能使用
- 例如：如果列表中有"强连通"但没有"强连通图"，就不能返回"强连通图"
- 如果当前批次中没有"握手定理"，就绝对不能返回"握手定理"
- 如果当前批次中没有"顶点的度数"，就绝对不能返回"顶点的度数"

示例：
- 题目："每个图中顶点的度数的总和等于边数的()倍"
- 知识点列表：["握手定理", "顶点的度数", "强连通"]
- 正确返回：{{"question_concepts": ["顶点的度数"], "option_b_concepts": ["握手定理"]}}
- 错误返回：{{"question_concepts": ["强连通图"], "option_b_concepts": ["连通图"]}}  # 这些不在列表中

当前批次的约束检查：
- 如果当前批次不包含"握手定理"，则所有选项的concepts都不能包含"握手定理"
- 如果当前批次不包含"顶点的度数"，则所有选项的concepts都不能包含"顶点的度数"
- 只能返回当前批次中实际存在的知识点名称
"""
        
        return prompt
    
    def simulate_llm_response(self, question: Dict, knowledge_batch: List[str]) -> Dict:
        """模拟大模型响应（单题版本）"""
        # 简单的关键词匹配逻辑
        question_text = str(question.get('question', '')).lower()
        option_a = str(question.get('option_a', '')).lower()
        option_b = str(question.get('option_b', '')).lower()
        option_c = str(question.get('option_c', '')).lower()
        option_d = str(question.get('option_d', '')).lower()
        
        # 为题目和选项找到匹配的知识点
        question_concepts = [kp for kp in knowledge_batch if kp.lower() in question_text]
        option_a_concepts = [kp for kp in knowledge_batch if kp.lower() in option_a]
        option_b_concepts = [kp for kp in knowledge_batch if kp.lower() in option_b]
        option_c_concepts = [kp for kp in knowledge_batch if kp.lower() in option_c]
        option_d_concepts = [kp for kp in knowledge_batch if kp.lower() in option_d]
        
        return {
            "question_id": question.get('id', 0),
            "question_concepts": question_concepts,
            "option_a_concepts": option_a_concepts,
            "option_b_concepts": option_b_concepts,
            "option_c_concepts": option_c_concepts,
            "option_d_concepts": option_d_concepts
        }
    
    def call_llm_api(self, prompt: str, question: Dict, knowledge_batch: List[str]) -> Dict:
        """调用通义千问API（单题版本）"""
        if self.chat_llm is None:
            self.logger.warning("通义千问客户端未初始化，使用模拟响应")
            return self.simulate_llm_response(question, knowledge_batch)
        
        try:
            messages = [
                {"role": "system", "content": "你是一个图论专家，具有深厚的图论理论基础和丰富的教学经验。请严格按照要求的JSON格式返回结果，准确分析题目和选项对应的知识点。"},
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
                
                # 解析JSON
                try:
                    result = json.loads(json_content)
                    return result
                except json.JSONDecodeError as e:
                    self.logger.error(f"JSON解析失败: {e}")
                    self.logger.error(f"原始内容: {json_content}")
                    return self.simulate_llm_response(question, knowledge_batch)
            else:
                # 如果没有找到JSON，返回模拟响应
                self.logger.warning("响应中未找到JSON格式，使用模拟响应")
                return self.simulate_llm_response(question, knowledge_batch)
                
        except Exception as e:
            self.logger.error(f"通义千问调用失败: {e}")
            # 返回模拟响应
            return self.simulate_llm_response(question, knowledge_batch)
    
    def process_questions(self, batch_size: int = 10) -> Dict:
        """处理所有题目，分批询问大模型"""
        if self.questions_data is None:
            return {}
        
        # 获取列名
        columns = self.questions_data.columns.tolist()
        print(f"题目文件列名: {columns}")
        
        # 假设列结构为：题目编号, 题目内容, 选项A, 选项B, 选项C, 选项D, 答案
        if len(columns) >= 6:
            question_col = columns[1]  # 题目内容列
            options_cols = columns[2:6]  # 选项列
            answer_col = columns[6] if len(columns) > 6 else None
        else:
            print("题目文件格式不符合预期")
            return {}
        
        # 准备题目数据
        questions = []
        for idx, row in self.questions_data.iterrows():
            question_id = row[columns[0]] if len(columns) > 0 else idx + 1
            questions.append({
                'id': question_id,
                'question': str(row[question_col]),
                'option_a': str(row[options_cols[0]]),
                'option_b': str(row[options_cols[1]]),
                'option_c': str(row[options_cols[2]]),
                'option_d': str(row[options_cols[3]]),
                'answer': row[answer_col] if answer_col else None
            })
        
        # 分批处理
        knowledge_batches = self.batch_knowledge_points(batch_size)
        all_mappings = {}
        
        print(f"开始逐题处理，共 {len(questions)} 道题目，{len(knowledge_batches)} 批知识点")
        
        # 为每道题初始化映射结果
        for question in questions:
            all_mappings[question['id']] = {
                'question_concepts': [],
                'option_a_concepts': [],
                'option_b_concepts': [],
                'option_c_concepts': [],
                'option_d_concepts': []
            }
        
        # 逐题处理
        for question_idx, question in enumerate(questions, 1):
            print(f"处理题目 {question_idx}/{len(questions)}: {question['question'][:50]}...")
            
            # 对每道题，遍历所有知识点批次
            for batch_idx, knowledge_batch in enumerate(knowledge_batches, 1):
                print(f"  批次 {batch_idx}/{len(knowledge_batches)}: {len(knowledge_batch)} 个知识点")
                print(f"    知识点列表: {knowledge_batch}")
                
                # 创建提示词
                prompt = self.create_llm_prompt(question, knowledge_batch)
                
                # 调用大模型
                try:
                    response = self.call_llm_api(prompt, question, knowledge_batch)
                    
                    # 处理响应
                    if 'question_id' in response:
                        question_id = response['question_id']
                        
                        # 合并知识点
                        all_mappings[question_id]['question_concepts'].extend(response.get('question_concepts', []))
                        all_mappings[question_id]['option_a_concepts'].extend(response.get('option_a_concepts', []))
                        all_mappings[question_id]['option_b_concepts'].extend(response.get('option_b_concepts', []))
                        all_mappings[question_id]['option_c_concepts'].extend(response.get('option_c_concepts', []))
                        all_mappings[question_id]['option_d_concepts'].extend(response.get('option_d_concepts', []))
                    
                    # 添加延迟避免API限制
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"  处理题目 {question_idx} 批次 {batch_idx} 时出错: {e}")
                    continue
        
        # 去重并整理结果
        self.mapping_results = {}
        for question_id, mappings in all_mappings.items():
            self.mapping_results[question_id] = {
                'question': questions[question_id - 1]['question'],
                'question_concepts': list(set(mappings['question_concepts'])),
                'option_a': questions[question_id - 1]['option_a'],
                'option_a_concepts': list(set(mappings['option_a_concepts'])),
                'option_b': questions[question_id - 1]['option_b'],
                'option_b_concepts': list(set(mappings['option_b_concepts'])),
                'option_c': questions[question_id - 1]['option_c'],
                'option_c_concepts': list(set(mappings['option_c_concepts'])),
                'option_d': questions[question_id - 1]['option_d'],
                'option_d_concepts': list(set(mappings['option_d_concepts'])),
                'answer': questions[question_id - 1]['answer']
            }
        
        return self.mapping_results
    
    def save_mapping_results(self, output_file: str = "question_knowledge_mapping_v2.json"):
        """保存映射结果到文件"""
        if self.mapping_results is None:
            print("请先执行映射操作")
            return
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.mapping_results, f, ensure_ascii=False, indent=2)
        
        print(f"映射结果已保存到: {output_file}")
    
    def generate_summary_report(self) -> str:
        """生成总结报告"""
        if self.mapping_results is None:
            return "请先执行映射操作"
        
        # 统计信息
        total_questions = len(self.mapping_results)
        total_concepts = len(self.knowledge_points)
        
        # 统计知识点使用频率
        concept_usage = Counter()
        for result in self.mapping_results.values():
            for concepts in [result['question_concepts'], result['option_a_concepts'], 
                           result['option_b_concepts'], result['option_c_concepts'], 
                           result['option_d_concepts']]:
                concept_usage.update(concepts)
        
        # 生成报告
        report = []
        report.append("# 图论选择题与知识图谱映射总结报告\n")
        report.append(f"## 基本统计")
        report.append(f"- 总题目数: {total_questions}")
        report.append(f"- 总知识点数: {total_concepts}")
        report.append(f"- 被使用的知识点数: {len(concept_usage)}")
        report.append(f"- 知识点使用率: {len(concept_usage)/total_concepts*100:.1f}%\n")
        
        report.append("## 最常用的知识点（前20个）")
        for concept, count in concept_usage.most_common(20):
            report.append(f"- {concept}: {count} 次")
        
        report.append("\n## 题目映射详情")
        for question_id, result in self.mapping_results.items():
            report.append(f"\n### 题目 {question_id}")
            report.append(f"**题目:** {result['question']}")
            report.append(f"**题目相关知识点:** {', '.join(result['question_concepts']) if result['question_concepts'] else '无'}")
            report.append(f"**选项A:** {result['option_a']}")
            report.append(f"**选项A相关知识点:** {', '.join(result['option_a_concepts']) if result['option_a_concepts'] else '无'}")
            report.append(f"**选项B:** {result['option_b']}")
            report.append(f"**选项B相关知识点:** {', '.join(result['option_b_concepts']) if result['option_b_concepts'] else '无'}")
            report.append(f"**选项C:** {result['option_c']}")
            report.append(f"**选项C相关知识点:** {', '.join(result['option_c_concepts']) if result['option_c_concepts'] else '无'}")
            report.append(f"**选项D:** {result['option_d']}")
            report.append(f"**选项D相关知识点:** {', '.join(result['option_d_concepts']) if result['option_d_concepts'] else '无'}")
            if result['answer']:
                report.append(f"**答案:** {result['answer']}")
        
        return "\n".join(report)

def main():
    """主函数"""
    # 初始化映射器
    mapper = QuestionKnowledgeMapperV2("questions.csv", "optimized_knowledge_graph.csv",api_key="sk-c39ae8196c154979bc958d0dde69633b")
    
    # 执行映射
    print("开始执行题目-知识点映射...")
    mapping_results = mapper.process_questions(batch_size=10)
    
    # 生成报告
    report = mapper.generate_summary_report()
    print(report)
    
    # 保存结果
    mapper.save_mapping_results()
    
    print("映射完成！")

if __name__ == "__main__":
    main()
