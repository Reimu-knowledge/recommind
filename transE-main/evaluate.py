import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Set
import logging
from tqdm import tqdm
from collections import defaultdict
import time

from model import TransE
from data_manager import DataManager

class Evaluator:
    """TransE模型评估器"""
    
    def __init__(self, data_manager: DataManager, args):
        self.data_manager = data_manager
        self.args = args
        self.device = torch.device(f'cuda:{args.gpu}' if args.gpu >= 0 and torch.cuda.is_available() else 'cpu')
        
        # 构建所有三元组的集合（用于过滤评估）
        self.all_triplets = data_manager.all_triplets
    
    def evaluate(self, model: TransE, dataloader) -> Dict[str, float]:
        """评估模型性能"""
        model.eval()
        
        all_ranks = []
        all_hits_at_k = defaultdict(list)
        
        with torch.no_grad():
            for batch in tqdm(dataloader, desc="Evaluating"):
                positive_triplets = batch['positive']
                
                for i in range(positive_triplets.size(0)):
                    h, r, t = positive_triplets[i].tolist()
                    
                    # 预测头实体
                    head_ranks, head_hits = self._predict_entity(
                        model, h, r, t, target_entity=h, predict_head=True
                    )
                    
                    # 预测尾实体
                    tail_ranks, tail_hits = self._predict_entity(
                        model, h, r, t, target_entity=t, predict_head=False
                    )
                    
                    # 记录结果
                    all_ranks.extend([head_ranks, tail_ranks])
                    
                    for k in self.args.hits_at_k:
                        all_hits_at_k[f'hits_at_{k}'].extend([head_hits[k], tail_hits[k]])
        
        # 计算指标
        metrics = self._compute_metrics(all_ranks, all_hits_at_k)
        
        return metrics
    
    def _predict_entity(self, model: TransE, h: int, r: int, t: int, 
                       target_entity: int, predict_head: bool = False) -> Tuple[float, Dict[int, bool]]:
        """预测实体（头实体或尾实体）"""
        model.eval()
        
        # 获取所有候选实体
        all_entities = list(range(self.data_manager.num_entities))
        
        # 计算所有候选的得分
        scores = []
        
        if predict_head:
            # 预测头实体，固定关系和尾实体
            for candidate_h in all_entities:
                score = model.predict(
                    torch.tensor([candidate_h], device=self.device),
                    torch.tensor([r], device=self.device),
                    torch.tensor([t], device=self.device)
                )
                scores.append(score.item())
        else:
            # 预测尾实体，固定头实体和关系
            for candidate_t in all_entities:
                score = model.predict(
                    torch.tensor([h], device=self.device),
                    torch.tensor([r], device=self.device),
                    torch.tensor([candidate_t], device=self.device)
                )
                scores.append(score.item())
        
        # 转换为numpy数组
        scores = np.array(scores)
        
        # 过滤评估：移除训练集中的有效三元组
        if self.args.filtered_eval:
            scores = self._filter_scores(scores, h, r, t, predict_head)
        
        # 计算排名
        rank = self._compute_rank(scores, target_entity, predict_head)
        
        # 计算Hits@K
        hits_at_k = {}
        for k in self.args.hits_at_k:
            hits_at_k[k] = rank <= k
        
        return rank, hits_at_k
    
    def _filter_scores(self, scores: np.ndarray, h: int, r: int, t: int, 
                      predict_head: bool) -> np.ndarray:
        """过滤评估：将训练集中的有效三元组得分设为负无穷"""
        filtered_scores = scores.copy()
        
        if predict_head:
            # 预测头实体时，过滤掉所有有效的(h', r, t)三元组
            for candidate_h in range(len(scores)):
                if (candidate_h, r, t) in self.all_triplets:
                    filtered_scores[candidate_h] = float('-inf')
        else:
            # 预测尾实体时，过滤掉所有有效的(h, r, t')三元组
            for candidate_t in range(len(scores)):
                if (h, r, candidate_t) in self.all_triplets:
                    filtered_scores[candidate_t] = float('-inf')
        
        return filtered_scores
    
    def _compute_rank(self, scores: np.ndarray, target_entity: int, predict_head: bool) -> float:
        """计算目标实体的排名"""
        # 获取目标实体的得分
        target_score = scores[target_entity]
        
        # 计算排名（得分大于目标得分的实体数量 + 1）
        rank = np.sum(scores > target_score) + 1
        
        return rank
    
    def _compute_metrics(self, ranks: List[float], hits_at_k: Dict[str, List[bool]]) -> Dict[str, float]:
        """计算评估指标"""
        ranks = np.array(ranks)
        
        # 计算MRR (Mean Reciprocal Rank)
        mrr = np.mean(1.0 / ranks)
        
        # 计算Hits@K
        metrics = {'mrr': mrr}
        for k, hits in hits_at_k.items():
            metrics[k] = np.mean(hits)
        
        # 计算平均排名
        metrics['mean_rank'] = np.mean(ranks)
        metrics['median_rank'] = np.median(ranks)
        
        return metrics
    
    def evaluate_triplet(self, model: TransE, h: int, r: int, t: int) -> Dict[str, float]:
        """评估单个三元组"""
        model.eval()
        
        with torch.no_grad():
            # 计算三元组的得分
            score = model.predict(
                torch.tensor([h], device=self.device),
                torch.tensor([r], device=self.device),
                torch.tensor([t], device=self.device)
            )
            
            # 计算距离
            h_emb = model.get_entity_embedding(torch.tensor([h], device=self.device))
            r_emb = model.get_relation_embedding(torch.tensor([r], device=self.device))
            t_emb = model.get_entity_embedding(torch.tensor([t], device=self.device))
            
            if model.distance_metric == 'L1':
                distance = torch.norm(h_emb + r_emb - t_emb, p=1)
            else:
                distance = torch.norm(h_emb + r_emb - t_emb, p=2)
        
        return {
            'score': score.item(),
            'distance': distance.item()
        }
    
    def get_top_k_predictions(self, model: TransE, h: int, r: int, k: int = 10) -> List[Tuple[int, float]]:
        """获取前K个尾实体预测"""
        model.eval()
        
        scores = []
        entities = []
        
        with torch.no_grad():
            for t in range(self.data_manager.num_entities):
                score = model.predict(
                    torch.tensor([h], device=self.device),
                    torch.tensor([r], device=self.device),
                    torch.tensor([t], device=self.device)
                )
                scores.append(score.item())
                entities.append(t)
        
        # 排序并返回前K个
        sorted_indices = np.argsort(scores)[::-1]  # 降序排列
        top_k = [(entities[i], scores[i]) for i in sorted_indices[:k]]
        
        return top_k
    
    def get_top_k_head_predictions(self, model: TransE, r: int, t: int, k: int = 10) -> List[Tuple[int, float]]:
        """获取前K个头实体预测"""
        model.eval()
        
        scores = []
        entities = []
        
        with torch.no_grad():
            for h in range(self.data_manager.num_entities):
                score = model.predict(
                    torch.tensor([h], device=self.device),
                    torch.tensor([r], device=self.device),
                    torch.tensor([t], device=self.device)
                )
                scores.append(score.item())
                entities.append(h)
        
        # 排序并返回前K个
        sorted_indices = np.argsort(scores)[::-1]  # 降序排列
        top_k = [(entities[i], scores[i]) for i in sorted_indices[:k]]
        
        return top_k
    
    def print_evaluation_summary(self, metrics: Dict[str, float]):
        """打印评估结果摘要"""
        logging.info("=" * 50)
        logging.info("评估结果摘要")
        logging.info("=" * 50)
        logging.info(f"MRR: {metrics['mrr']:.4f}")
        logging.info(f"Mean Rank: {metrics['mean_rank']:.2f}")
        logging.info(f"Median Rank: {metrics['median_rank']:.2f}")
        
        for k in self.args.hits_at_k:
            if f'hits_at_{k}' in metrics:
                logging.info(f"Hits@{k}: {metrics[f'hits_at_{k}']:.4f}")
        
        logging.info("=" * 50) 