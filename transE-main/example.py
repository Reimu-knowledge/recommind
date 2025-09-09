#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransE 使用示例
演示如何使用TransE项目进行知识图谱嵌入
"""

import os
import time
import sys
import logging
import pandas as pd
import numpy as np
import torch
from args import get_args
from data_manager import DataManager
from model import TransE
from train import Trainer
from evaluate import Evaluator
from utils import (
    setup_logging, save_experiment_config, print_experiment_summary,
    save_results_summary, set_random_seed, count_parameters, format_time,
    plot_training_curves, save_embeddings, create_sample_data
)

def create_sample_knowledge_graph():
    """创建一个示例知识图谱"""
    # 实体
    entities = [
        "北京", "上海", "广州", "深圳", "杭州", "南京", "武汉", "成都", "西安", "重庆",
        "中国", "美国", "日本", "英国", "法国", "德国", "俄罗斯", "加拿大", "澳大利亚", "巴西",
        "清华大学", "北京大学", "复旦大学", "上海交通大学", "浙江大学", "南京大学", "武汉大学", "四川大学", "西安交通大学", "重庆大学",
        "计算机科学", "人工智能", "机器学习", "深度学习", "自然语言处理", "计算机视觉", "数据挖掘", "软件工程", "网络技术", "数据库"
    ]
    
    # 关系
    relations = [
        "位于", "首都", "属于", "包含", "研究", "教授", "学习", "工作", "合作", "影响"
    ]
    
    # 生成三元组
    triplets = []
    
    # 地理位置关系
    triplets.extend([
        ["北京", "位于", "中国"],
        ["上海", "位于", "中国"],
        ["广州", "位于", "中国"],
        ["深圳", "位于", "中国"],
        ["杭州", "位于", "中国"],
        ["南京", "位于", "中国"],
        ["武汉", "位于", "中国"],
        ["成都", "位于", "中国"],
        ["西安", "位于", "中国"],
        ["重庆", "位于", "中国"],
        ["北京", "首都", "中国"],
    ])
    
    # 大学关系
    triplets.extend([
        ["清华大学", "位于", "北京"],
        ["北京大学", "位于", "北京"],
        ["复旦大学", "位于", "上海"],
        ["上海交通大学", "位于", "上海"],
        ["浙江大学", "位于", "杭州"],
        ["南京大学", "位于", "南京"],
        ["武汉大学", "位于", "武汉"],
        ["四川大学", "位于", "成都"],
        ["西安交通大学", "位于", "西安"],
        ["重庆大学", "位于", "重庆"],
    ])
    
    # 学科关系
    triplets.extend([
        ["清华大学", "研究", "计算机科学"],
        ["北京大学", "研究", "人工智能"],
        ["复旦大学", "研究", "机器学习"],
        ["上海交通大学", "研究", "深度学习"],
        ["浙江大学", "研究", "自然语言处理"],
        ["南京大学", "研究", "计算机视觉"],
        ["武汉大学", "研究", "数据挖掘"],
        ["四川大学", "研究", "软件工程"],
        ["西安交通大学", "研究", "网络技术"],
        ["重庆大学", "研究", "数据库"],
    ])
    
    # 教授关系
    triplets.extend([
        ["清华大学", "教授", "计算机科学"],
        ["北京大学", "教授", "人工智能"],
        ["复旦大学", "教授", "机器学习"],
        ["上海交通大学", "教授", "深度学习"],
        ["浙江大学", "教授", "自然语言处理"],
        ["南京大学", "教授", "计算机视觉"],
        ["武汉大学", "教授", "数据挖掘"],
        ["四川大学", "教授", "软件工程"],
        ["西安交通大学", "教授", "网络技术"],
        ["重庆大学", "教授", "数据库"],
    ])
    
    # 学习关系
    triplets.extend([
        ["计算机科学", "学习", "人工智能"],
        ["人工智能", "学习", "机器学习"],
        ["机器学习", "学习", "深度学习"],
        ["深度学习", "学习", "自然语言处理"],
        ["深度学习", "学习", "计算机视觉"],
        ["数据挖掘", "学习", "机器学习"],
        ["软件工程", "学习", "计算机科学"],
        ["网络技术", "学习", "计算机科学"],
        ["数据库", "学习", "计算机科学"],
    ])
    
    # 工作关系
    triplets.extend([
        ["清华大学", "工作", "北京"],
        ["北京大学", "工作", "北京"],
        ["复旦大学", "工作", "上海"],
        ["上海交通大学", "工作", "上海"],
        ["浙江大学", "工作", "杭州"],
        ["南京大学", "工作", "南京"],
        ["武汉大学", "工作", "武汉"],
        ["四川大学", "工作", "成都"],
        ["西安交通大学", "工作", "西安"],
        ["重庆大学", "工作", "重庆"],
    ])
    
    # 合作关系
    triplets.extend([
        ["清华大学", "合作", "北京大学"],
        ["复旦大学", "合作", "上海交通大学"],
        ["浙江大学", "合作", "南京大学"],
        ["武汉大学", "合作", "四川大学"],
        ["西安交通大学", "合作", "重庆大学"],
        ["计算机科学", "合作", "人工智能"],
        ["机器学习", "合作", "深度学习"],
        ["自然语言处理", "合作", "计算机视觉"],
    ])
    
    # 影响关系
    triplets.extend([
        ["计算机科学", "影响", "人工智能"],
        ["人工智能", "影响", "机器学习"],
        ["机器学习", "影响", "深度学习"],
        ["深度学习", "影响", "自然语言处理"],
        ["深度学习", "影响", "计算机视觉"],
        ["清华大学", "影响", "计算机科学"],
        ["北京大学", "影响", "人工智能"],
    ])
    
    return triplets

def run_transe_example():
    """运行TransE示例"""
    logging.info("=" * 60)
    logging.info("TransE 知识图谱嵌入示例")
    logging.info("=" * 60)
    
    # 创建示例数据
    logging.info("1. 创建示例知识图谱...")
    triplets = create_sample_knowledge_graph()
    
    # 保存为CSV文件
    sample_data_path = "sample_knowledge_graph.csv"
    df = pd.DataFrame(triplets, columns=['head', 'relation', 'tail'])
    df.to_csv(sample_data_path, index=False, header=False)
    
    logging.info(f"   创建了 {len(triplets)} 个三元组")
    logging.info(f"   包含 {len(set(df['head'].unique()) | set(df['tail'].unique()))} 个实体")
    logging.info(f"   包含 {len(df['relation'].unique())} 个关系")
    logging.info(f"   数据已保存到: {sample_data_path}")
    
    # 设置参数
    logging.info("\n2. 设置训练参数...")
    sys.argv = [
        'example.py',
        '--data_path', sample_data_path,
        '--embedding_dim', '50',
        '--margin', '1.0',
        '--distance_metric', 'L1',
        '--learning_rate', '0.01',
        '--batch_size', '32',
        '--epochs', '100',
        '--gpu', '-1',  # 使用CPU
        '--filtered_eval',
        '--save_dir', './example_results'
    ]
    
    args = get_args()
    
    # 设置随机种子
    set_random_seed(args.seed)
    
    # 设置日志
    results_dir, log_file = setup_logging(args.save_dir)
    args.save_dir = results_dir
    
    # 打印实验摘要
    print_experiment_summary(args)
    
    # 保存实验配置
    save_experiment_config(args, results_dir)
    
    # 初始化数据管理器
    logging.info("\n3. 初始化数据管理器...")
    data_manager = DataManager(
        data_path=args.data_path,
        delimiter=args.delimiter,
        header=args.header,
        train_ratio=args.train_ratio,
        valid_ratio=args.valid_ratio,
        test_ratio=args.test_ratio,
        negative_samples=args.negative_samples
    )
    
    logging.info(f"   实体数量: {data_manager.num_entities}")
    logging.info(f"   关系数量: {data_manager.num_relations}")
    logging.info(f"   训练三元组: {len(data_manager.train_triplets)}")
    logging.info(f"   验证三元组: {len(data_manager.valid_triplets)}")
    logging.info(f"   测试三元组: {len(data_manager.test_triplets)}")
    
    # 初始化模型
    logging.info("\n4. 初始化TransE模型...")
    model = TransE(
        num_entities=data_manager.num_entities,
        num_relations=data_manager.num_relations,
        embedding_dim=args.embedding_dim,
        margin=args.margin,
        distance_metric=args.distance_metric,
        normalize_embeddings=args.normalize_embeddings
    )
    
    logging.info(f"   模型参数数量: {count_parameters(model):,}")
    
    # 获取数据加载器
    train_loader, valid_loader, test_loader = data_manager.get_dataloaders(
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )
    
    # 初始化训练器
    trainer = Trainer(model, data_manager, args)
    
    # 开始训练
    logging.info("\n5. 开始训练...")
    start_time = time.time()
    
    training_history = trainer.train(train_loader, valid_loader)
    
    training_time = time.time() - start_time
    logging.info(f"   训练完成，总时间: {format_time(training_time)}")
    
    # 加载最佳模型
    trainer.load_best_model()
    
    # 在测试集上评估
    logging.info("\n6. 评估模型性能...")
    evaluator = Evaluator(data_manager, args)
    test_metrics = evaluator.evaluate(model, test_loader)
    
    # 打印测试结果
    evaluator.print_evaluation_summary(test_metrics)
    
    # 保存结果
    results = {
        'test_metrics': test_metrics,
        'training_history': training_history,
        'training_time': training_time,
        'model_info': {
            'num_entities': data_manager.num_entities,
            'num_relations': data_manager.num_relations,
            'embedding_dim': args.embedding_dim,
            'total_parameters': count_parameters(model)
        }
    }
    
    save_results_summary(results, results_dir)
    
    # 绘制训练曲线
    plot_training_curves(training_history, results_dir)
    
    # 保存嵌入
    save_embeddings(model, data_manager, results_dir)
    
    # 示例预测
    logging.info("\n7. 进行示例预测...")
    demonstrate_predictions(model, data_manager, evaluator, results_dir)
    
    logging.info(f"\n实验完成！结果保存在: {results_dir}")
    logging.info(f"日志文件: {log_file}")
    
    # 清理临时文件
    if os.path.exists(sample_data_path):
        os.remove(sample_data_path)
        logging.info(f"临时文件已清理: {sample_data_path}")

def demonstrate_predictions(model, data_manager, evaluator, results_dir):
    """演示预测功能"""
    # 选择一些测试三元组进行演示
    test_triplets = data_manager.test_triplets[:3]  # 取前3个测试三元组
    
    predictions = []
    for h, r, t in test_triplets:
        # 获取实体和关系的名称
        h_name = data_manager.get_entity_name(h)
        r_name = data_manager.get_relation_name(r)
        t_name = data_manager.get_entity_name(t)
        
        # 评估三元组
        triplet_metrics = evaluator.evaluate_triplet(model, h, r, t)
        
        # 获取前3个尾实体预测
        top_tail_predictions = evaluator.get_top_k_predictions(model, h, r, k=3)
        top_tail_names = [(data_manager.get_entity_name(t_id), score) for t_id, score in top_tail_predictions]
        
        # 获取前3个头实体预测
        top_head_predictions = evaluator.get_top_k_head_predictions(model, r, t, k=3)
        top_head_names = [(data_manager.get_entity_name(h_id), score) for h_id, score in top_head_predictions]
        
        prediction_info = {
            'triplet': f"({h_name}, {r_name}, {t_name})",
            'score': triplet_metrics['score'],
            'distance': triplet_metrics['distance'],
            'top_tail_predictions': top_tail_names,
            'top_head_predictions': top_head_names
        }
        predictions.append(prediction_info)
    
    # 保存预测结果
    import json
    predictions_file = os.path.join(results_dir, "sample_predictions.json")
    with open(predictions_file, 'w', encoding='utf-8') as f:
        json.dump(predictions, f, indent=2, ensure_ascii=False)
    
    # 打印一些预测结果
    logging.info("示例预测结果:")
    for i, pred in enumerate(predictions):
        logging.info(f"三元组 {i+1}: {pred['triplet']}")
        logging.info(f"  得分: {pred['score']:.4f}, 距离: {pred['distance']:.4f}")
        logging.info(f"  前3个尾实体预测:")
        for j, (name, score) in enumerate(pred['top_tail_predictions']):
            logging.info(f"    {j+1}. {name}: {score:.4f}")
        logging.info(f"  前3个头实体预测:")
        for j, (name, score) in enumerate(pred['top_head_predictions']):
            logging.info(f"    {j+1}. {name}: {score:.4f}")
        logging.info("")

if __name__ == "__main__":
    run_transe_example() 