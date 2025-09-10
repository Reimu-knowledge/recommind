#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransE 快速测试脚本
验证项目的基本功能是否正常工作
"""

import os
import sys
import torch
import numpy as np
import pandas as pd
from args import get_args
from data_manager import DataManager
from model import TransE
from train import Trainer
from evaluate import Evaluator
from utils import set_random_seed, count_parameters

def create_mini_test_data():
    """创建小型测试数据"""
    triplets = [
        ["A", "R1", "B"],
        ["B", "R1", "C"],
        ["C", "R2", "D"],
        ["D", "R2", "E"],
        ["A", "R3", "D"],
        ["B", "R3", "E"],
    ]
    
    # 保存为临时文件
    test_file = "mini_test_data.csv"
    df = pd.DataFrame(triplets, columns=['head', 'relation', 'tail'])
    df.to_csv(test_file, index=False, header=False)
    return test_file

def test_data_manager():
    """测试数据管理器"""
    print("测试数据管理器...")
    
    test_file = create_mini_test_data()
    
    try:
        data_manager = DataManager(
            data_path=test_file,
            train_ratio=0.6,
            valid_ratio=0.2,
            test_ratio=0.2,
            negative_samples=1
        )
        
        print(f"  ✓ 实体数量: {data_manager.num_entities}")
        print(f"  ✓ 关系数量: {data_manager.num_relations}")
        print(f"  ✓ 训练三元组: {len(data_manager.train_triplets)}")
        print(f"  ✓ 验证三元组: {len(data_manager.valid_triplets)}")
        print(f"  ✓ 测试三元组: {len(data_manager.test_triplets)}")
        
        # 测试数据加载器
        train_loader, valid_loader, test_loader = data_manager.get_dataloaders(
            batch_size=2, num_workers=0
        )
        
        print(f"  ✓ 数据加载器创建成功")
        
        # 清理临时文件
        os.remove(test_file)
        
        return data_manager
        
    except Exception as e:
        print(f"  ✗ 数据管理器测试失败: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return None

def test_model():
    """测试TransE模型"""
    print("测试TransE模型...")
    
    try:
        model = TransE(
            num_entities=10,
            num_relations=5,
            embedding_dim=20,
            margin=1.0,
            distance_metric='L1',
            normalize_embeddings=True
        )
        
        print(f"  ✓ 模型创建成功")
        print(f"  ✓ 参数数量: {count_parameters(model):,}")
        
        # 测试前向传播
        positive_triplets = torch.tensor([[0, 0, 1], [1, 0, 2]])
        negative_triplets = torch.tensor([[0, 0, 3], [1, 0, 4]])
        
        loss = model(positive_triplets, negative_triplets)
        print(f"  ✓ 前向传播成功，损失: {loss.item():.4f}")
        
        # 测试预测
        scores = model.predict(
            torch.tensor([0]),
            torch.tensor([0]),
            torch.tensor([1])
        )
        print(f"  ✓ 预测功能正常，得分: {scores.item():.4f}")
        
        return model
        
    except Exception as e:
        print(f"  ✗ 模型测试失败: {e}")
        return None

def test_training():
    """测试训练功能"""
    print("测试训练功能...")
    
    # 创建测试数据
    test_file = create_mini_test_data()
    
    try:
        # 设置参数
        sys.argv = [
            'test_quick.py',
            '--data_path', test_file,
            '--embedding_dim', '10',
            '--margin', '1.0',
            '--distance_metric', 'L1',
            '--learning_rate', '0.01',
            '--batch_size', '2',
            '--epochs', '5',
            '--gpu', '-1'
        ]
        
        args = get_args()
        set_random_seed(args.seed)
        
        # 初始化数据管理器
        data_manager = DataManager(
            data_path=args.data_path,
            train_ratio=0.6,
            valid_ratio=0.2,
            test_ratio=0.2,
            negative_samples=1
        )
        
        # 初始化模型
        model = TransE(
            num_entities=data_manager.num_entities,
            num_relations=data_manager.num_relations,
            embedding_dim=args.embedding_dim,
            margin=args.margin,
            distance_metric=args.distance_metric,
            normalize_embeddings=args.normalize_embeddings
        )
        
        # 获取数据加载器
        train_loader, valid_loader, test_loader = data_manager.get_dataloaders(
            batch_size=args.batch_size, num_workers=0
        )
        
        # 初始化训练器
        trainer = Trainer(model, data_manager, args)
        
        # 训练一个epoch
        train_loss = trainer.train_epoch(train_loader)
        print(f"  ✓ 训练一个epoch成功，损失: {train_loss:.4f}")
        
        # 验证
        valid_metrics = trainer.validate(valid_loader)
        print(f"  ✓ 验证成功，损失: {valid_metrics['loss']:.4f}")
        
        # 清理临时文件
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"  ✗ 训练测试失败: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def test_evaluation():
    """测试评估功能"""
    print("测试评估功能...")
    
    # 创建测试数据
    test_file = create_mini_test_data()
    
    try:
        # 设置参数
        sys.argv = [
            'test_quick.py',
            '--data_path', test_file,
            '--embedding_dim', '10',
            '--margin', '1.0',
            '--distance_metric', 'L1',
            '--learning_rate', '0.01',
            '--batch_size', '2',
            '--epochs', '5',
            '--gpu', '-1'
        ]
        
        args = get_args()
        set_random_seed(args.seed)
        
        # 初始化数据管理器
        data_manager = DataManager(
            data_path=args.data_path,
            train_ratio=0.6,
            valid_ratio=0.2,
            test_ratio=0.2,
            negative_samples=1
        )
        
        # 初始化模型
        model = TransE(
            num_entities=data_manager.num_entities,
            num_relations=data_manager.num_relations,
            embedding_dim=args.embedding_dim,
            margin=args.margin,
            distance_metric=args.distance_metric,
            normalize_embeddings=args.normalize_embeddings
        )
        
        # 获取数据加载器
        train_loader, valid_loader, test_loader = data_manager.get_dataloaders(
            batch_size=args.batch_size, num_workers=0
        )
        
        # 初始化评估器
        evaluator = Evaluator(data_manager, args)
        
        # 评估单个三元组
        h, r, t = data_manager.test_triplets[0]
        triplet_metrics = evaluator.evaluate_triplet(model, h, r, t)
        print(f"  ✓ 单个三元组评估成功，得分: {triplet_metrics['score']:.4f}")
        
        # 获取预测
        top_predictions = evaluator.get_top_k_predictions(model, h, r, k=3)
        print(f"  ✓ 获取前K预测成功，预测数量: {len(top_predictions)}")
        
        # 清理临时文件
        os.remove(test_file)
        
        return True
        
    except Exception as e:
        print(f"  ✗ 评估测试失败: {e}")
        if os.path.exists(test_file):
            os.remove(test_file)
        return False

def main():
    """主测试函数"""
    print("=" * 50)
    print("TransE 项目快速测试")
    print("=" * 50)
    
    # 测试各个模块
    tests = [
        ("数据管理器", test_data_manager),
        ("TransE模型", test_model),
        ("训练功能", test_training),
        ("评估功能", test_evaluation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if test_func():
                passed += 1
                print(f"  ✓ {test_name} 测试通过")
            else:
                print(f"  ✗ {test_name} 测试失败")
        except Exception as e:
            print(f"  ✗ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！项目可以正常使用。")
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
    
    print("=" * 50)

if __name__ == "__main__":
    main() 