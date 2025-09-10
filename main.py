#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransE 知识图谱嵌入主程序
基于论文: Translating Embeddings for Modeling Multi-relational Data
"""

import os
import sys
import torch
import logging
import time
from typing import Dict, List
import numpy as np

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

def main():
    """主函数"""
    # 解析参数
    args = get_args()
    
    # 设置随机种子
    set_random_seed(args.seed)
    
    # 设置日志和结果目录
    results_dir, log_file = setup_logging(args.save_dir)
    
    # 更新args中的save_dir为实际的结果目录
    args.save_dir = results_dir
    
    # 打印实验摘要
    print_experiment_summary(args)
    
    # 保存实验配置
    save_experiment_config(args, results_dir)
    
    # 检查数据文件是否存在
    if not os.path.exists(args.data_path):
        logging.error(f"数据文件不存在: {args.data_path}")
        logging.info("创建示例数据用于测试...")
        sample_data_path = os.path.join(results_dir, "sample_data.csv")
        create_sample_data(sample_data_path, num_entities=100, num_relations=10, num_triplets=1000)
        args.data_path = sample_data_path
    
    # 初始化数据管理器
    logging.info("初始化数据管理器...")
    data_manager = DataManager(
        data_path=args.data_path,
        delimiter=args.delimiter,
        header=args.header,
        train_ratio=args.train_ratio,
        valid_ratio=args.valid_ratio,
        test_ratio=args.test_ratio,
        negative_samples=args.negative_samples
    )
    
    logging.info(f"数据加载完成:")
    logging.info(f"  实体数量: {data_manager.num_entities}")
    logging.info(f"  关系数量: {data_manager.num_relations}")
    logging.info(f"  训练三元组: {len(data_manager.train_triplets)}")
    logging.info(f"  验证三元组: {len(data_manager.valid_triplets)}")
    logging.info(f"  测试三元组: {len(data_manager.test_triplets)}")
    
    # 初始化模型
    logging.info("初始化TransE模型...")
    model = TransE(
        num_entities=data_manager.num_entities,
        num_relations=data_manager.num_relations,
        embedding_dim=args.embedding_dim,
        margin=args.margin,
        distance_metric=args.distance_metric,
        normalize_embeddings=args.normalize_embeddings
    )
    
    logging.info(f"模型参数数量: {count_parameters(model):,}")
    
    # 获取数据加载器
    train_loader, valid_loader, test_loader = data_manager.get_dataloaders(
        batch_size=args.batch_size,
        num_workers=args.num_workers
    )
    
    # 初始化训练器
    trainer = Trainer(model, data_manager, args)
    
    # 开始训练
    logging.info("开始训练...")
    start_time = time.time()
    
    training_history = trainer.train(train_loader, valid_loader)
    
    training_time = time.time() - start_time
    logging.info(f"训练完成，总时间: {format_time(training_time)}")
    
    # 加载最佳模型
    trainer.load_best_model()
    
    # 在测试集上评估
    logging.info("在测试集上评估模型...")
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
    logging.info("进行示例预测...")
    _demonstrate_predictions(model, data_manager, evaluator, results_dir)
    
    logging.info(f"实验完成！结果保存在: {results_dir}")
    logging.info(f"日志文件: {log_file}")

def _demonstrate_predictions(model, data_manager, evaluator, results_dir):
    """演示预测功能"""
    # 选择一些测试三元组进行演示
    test_triplets = data_manager.test_triplets[:5]  # 取前5个测试三元组
    
    predictions = []
    for h, r, t in test_triplets:
        # 获取实体和关系的名称
        h_name = data_manager.get_entity_name(h)
        r_name = data_manager.get_relation_name(r)
        t_name = data_manager.get_entity_name(t)
        
        # 评估三元组
        triplet_metrics = evaluator.evaluate_triplet(model, h, r, t)
        
        # 获取前5个尾实体预测
        top_tail_predictions = evaluator.get_top_k_predictions(model, h, r, k=5)
        top_tail_names = [(data_manager.get_entity_name(t_id), score) for t_id, score in top_tail_predictions]
        
        # 获取前5个头实体预测
        top_head_predictions = evaluator.get_top_k_head_predictions(model, r, t, k=5)
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
        logging.info(f"  前5个尾实体预测:")
        for j, (name, score) in enumerate(pred['top_tail_predictions']):
            logging.info(f"    {j+1}. {name}: {score:.4f}")
        logging.info(f"  前5个头实体预测:")
        for j, (name, score) in enumerate(pred['top_head_predictions']):
            logging.info(f"    {j+1}. {name}: {score:.4f}")
        logging.info("")

if __name__ == "__main__":
    main() 