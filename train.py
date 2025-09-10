import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import logging
import time
from tqdm import tqdm
import numpy as np
from typing import Dict, List, Tuple
import os

from model import TransE
from data_manager import DataManager
from evaluate import Evaluator

class Trainer:
    """TransE模型训练器"""
    
    def __init__(self, model: TransE, data_manager: DataManager, args):
        self.model = model
        self.data_manager = data_manager
        self.args = args
        
        # 设置设备
        self.device = torch.device(f'cuda:{args.gpu}' if args.gpu >= 0 and torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        # 设置优化器
        self.optimizer = optim.Adam(self.model.parameters(), lr=args.learning_rate)
        
        # 设置学习率调度器
        if hasattr(args, 'use_scheduler') and args.use_scheduler:
            self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                factor=args.scheduler_factor,
                patience=args.scheduler_patience,
                min_lr=args.scheduler_min_lr
            )
        else:
            self.scheduler = None
        
        # 初始化评估器
        self.evaluator = Evaluator(data_manager, args)
        
        # 训练状态
        self.best_valid_score = float('inf')
        self.patience_counter = 0
        self.training_history = {
            'train_loss': [],
            'valid_loss': [],
            'valid_mrr': [],
            'valid_hits_at_10': []
        }
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """训练一个epoch"""
        self.model.train()
        total_loss = 0.0
        num_batches = 0
        
        progress_bar = tqdm(train_loader, desc="Training")
        
        for batch_idx, batch in enumerate(progress_bar):
            # 将数据移到设备上
            positive_triplets = batch['positive'].to(self.device)
            negative_triplets = batch['negative'].to(self.device)
            
            # 前向传播
            loss = self.model(positive_triplets, negative_triplets)
            
            # 反向传播
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
            
            # 归一化实体嵌入（按照论文算法）
            self.model.normalize_entity_embeddings()
            
            # 记录损失
            total_loss += loss.item()
            num_batches += 1
            
            # 更新进度条
            progress_bar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'avg_loss': f'{total_loss / num_batches:.4f}'
            })
            
            # 记录日志
            if batch_idx % self.args.log_interval == 0:
                logging.info(f"Batch {batch_idx}: Loss = {loss.item():.4f}")
        
        avg_loss = total_loss / num_batches
        return avg_loss
    
    def validate(self, valid_loader: DataLoader) -> Dict[str, float]:
        """验证模型"""
        self.model.eval()
        total_loss = 0.0
        num_batches = 0
        
        with torch.no_grad():
            for batch in tqdm(valid_loader, desc="Validating"):
                positive_triplets = batch['positive'].to(self.device)
                negative_triplets = batch['negative'].to(self.device)
                
                loss = self.model(positive_triplets, negative_triplets)
                total_loss += loss.item()
                num_batches += 1
        
        avg_loss = total_loss / num_batches
        
        # 进行链接预测评估
        metrics = self.evaluator.evaluate(self.model, valid_loader)
        metrics['loss'] = avg_loss
        
        return metrics
    
    def train(self, train_loader: DataLoader, valid_loader: DataLoader) -> Dict[str, List[float]]:
        """完整训练过程"""
        logging.info("开始训练TransE模型...")
        logging.info(f"设备: {self.device}")
        logging.info(f"模型参数数量: {sum(p.numel() for p in self.model.parameters()):,}")
        
        start_time = time.time()
        
        for epoch in range(self.args.epochs):
            epoch_start_time = time.time()
            
            # 训练一个epoch
            train_loss = self.train_epoch(train_loader)
            
            # 验证
            valid_metrics = self.validate(valid_loader)
            valid_loss = valid_metrics['loss']
            valid_mrr = valid_metrics.get('mrr', 0.0)
            valid_hits_at_10 = valid_metrics.get('hits_at_10', 0.0)
            
            # 更新学习率调度器
            if self.scheduler is not None:
                self.scheduler.step(valid_loss)
            
            # 记录训练历史
            self.training_history['train_loss'].append(train_loss)
            self.training_history['valid_loss'].append(valid_loss)
            self.training_history['valid_mrr'].append(valid_mrr)
            self.training_history['valid_hits_at_10'].append(valid_hits_at_10)
            
            # 计算epoch时间
            epoch_time = time.time() - epoch_start_time
            
            # 记录日志
            logging.info(f"Epoch {epoch + 1}/{self.args.epochs} "
                        f"({epoch_time:.2f}s): "
                        f"Train Loss: {train_loss:.4f}, "
                        f"Valid Loss: {valid_loss:.4f}, "
                        f"Valid MRR: {valid_mrr:.4f}, "
                        f"Valid Hits@10: {valid_hits_at_10:.4f}")
            
            # 早停检查
            if self._should_stop_early(valid_loss):
                logging.info(f"早停触发，在epoch {epoch + 1}停止训练")
                break
            
            # 保存最佳模型
            if valid_loss < self.best_valid_score:
                self.best_valid_score = valid_loss
                self.patience_counter = 0
                self._save_best_model()
                logging.info(f"保存最佳模型，验证损失: {valid_loss:.4f}")
            else:
                self.patience_counter += 1
            
            # 定期保存检查点
            if (epoch + 1) % self.args.save_interval == 0:
                self._save_checkpoint(epoch + 1)
        
        total_time = time.time() - start_time
        logging.info(f"训练完成，总时间: {total_time:.2f}s")
        
        return self.training_history
    
    def _should_stop_early(self, valid_loss: float) -> bool:
        """检查是否应该早停"""
        if valid_loss < self.best_valid_score - self.args.early_stopping_delta:
            self.patience_counter = 0
            return False
        else:
            self.patience_counter += 1
            return self.patience_counter >= self.args.early_stopping_patience
    
    def _save_best_model(self):
        """保存最佳模型"""
        model_path = os.path.join(self.args.save_dir, 'best_model.pth')
        # 将args转换为字典，避免保存argparse.Namespace
        args_dict = {}
        for key, value in vars(self.args).items():
            if isinstance(value, (int, float, str, bool, list)):
                args_dict[key] = value
            else:
                args_dict[key] = str(value)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'args': args_dict,
            'best_valid_score': self.best_valid_score,
            'training_history': self.training_history
        }, model_path)
    
    def _save_checkpoint(self, epoch: int):
        """保存检查点"""
        checkpoint_path = os.path.join(self.args.save_dir, f'checkpoint_epoch_{epoch}.pth')
        # 将args转换为字典，避免保存argparse.Namespace
        args_dict = {}
        for key, value in vars(self.args).items():
            if isinstance(value, (int, float, str, bool, list)):
                args_dict[key] = value
            else:
                args_dict[key] = str(value)
        
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'scheduler_state_dict': self.scheduler.state_dict() if self.scheduler else None,
            'args': args_dict,
            'best_valid_score': self.best_valid_score,
            'training_history': self.training_history
        }, checkpoint_path)
    
    def load_best_model(self):
        """加载最佳模型"""
        model_path = os.path.join(self.args.save_dir, 'best_model.pth')
        if os.path.exists(model_path):
            try:
                # 尝试使用 weights_only=False 加载（兼容旧版本）
                checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
            except:
                # 如果失败，只加载模型权重
                checkpoint = torch.load(model_path, map_location=self.device, weights_only=True)
                logging.warning("只加载模型权重，无法加载训练历史")
            
            self.model.load_state_dict(checkpoint['model_state_dict'])
            if 'best_valid_score' in checkpoint:
                self.best_valid_score = checkpoint['best_valid_score']
            if 'training_history' in checkpoint:
                self.training_history = checkpoint['training_history']
            logging.info(f"加载最佳模型，验证损失: {self.best_valid_score:.4f}")
            return True
        else:
            logging.warning("未找到最佳模型文件")
            return False
    
    def get_model(self):
        """获取训练好的模型"""
        return self.model 