import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math

class TransE(nn.Module):
    """
    TransE模型实现
    论文: Translating Embeddings for Modeling Multi-relational Data
    """
    
    def __init__(self, num_entities: int, num_relations: int, embedding_dim: int = 50,
                 margin: float = 1.0, distance_metric: str = 'L1', normalize_embeddings: bool = True):
        super(TransE, self).__init__()
        
        self.num_entities = num_entities
        self.num_relations = num_relations
        self.embedding_dim = embedding_dim
        self.margin = margin
        self.distance_metric = distance_metric
        self.normalize_embeddings = normalize_embeddings
        
        # 初始化嵌入层
        self.entity_embeddings = nn.Embedding(num_entities, embedding_dim)
        self.relation_embeddings = nn.Embedding(num_relations, embedding_dim)
        
        # 初始化参数
        self._init_embeddings()
    
    def _init_embeddings(self):
        """初始化嵌入参数"""
        # 按照论文中的初始化方法
        entity_init_bound = 6.0 / math.sqrt(self.embedding_dim)
        relation_init_bound = 6.0 / math.sqrt(self.embedding_dim)
        
        # 实体嵌入初始化
        nn.init.uniform_(self.entity_embeddings.weight, -entity_init_bound, entity_init_bound)
        
        # 关系嵌入初始化
        nn.init.uniform_(self.relation_embeddings.weight, -relation_init_bound, relation_init_bound)
        
        # 对关系嵌入进行L2归一化
        with torch.no_grad():
            self.relation_embeddings.weight.data = F.normalize(
                self.relation_embeddings.weight.data, p=2, dim=1
            )
    
    def _distance(self, h_emb, r_emb, t_emb):
        """计算距离函数"""
        if self.distance_metric == 'L1':
            return torch.norm(h_emb + r_emb - t_emb, p=1, dim=1)
        elif self.distance_metric == 'L2':
            return torch.norm(h_emb + r_emb - t_emb, p=2, dim=1)
        else:
            raise ValueError(f"不支持的距离度量: {self.distance_metric}")
    
    def forward(self, positive_triplets, negative_triplets):
        """
        前向传播
        Args:
            positive_triplets: 正样本三元组 (batch_size, 3)
            negative_triplets: 负样本三元组 (batch_size * negative_samples, 3)
        """
        batch_size = positive_triplets.size(0)
        
        # 获取嵌入
        h_pos = self.entity_embeddings(positive_triplets[:, 0])  # 头实体
        r_pos = self.relation_embeddings(positive_triplets[:, 1])  # 关系
        t_pos = self.entity_embeddings(positive_triplets[:, 2])  # 尾实体
        
        h_neg = self.entity_embeddings(negative_triplets[:, 0])
        r_neg = self.relation_embeddings(negative_triplets[:, 1])
        t_neg = self.entity_embeddings(negative_triplets[:, 2])
        
        # 如果需要对实体嵌入进行归一化
        if self.normalize_embeddings:
            h_pos = F.normalize(h_pos, p=2, dim=1)
            t_pos = F.normalize(t_pos, p=2, dim=1)
            h_neg = F.normalize(h_neg, p=2, dim=1)
            t_neg = F.normalize(t_neg, p=2, dim=1)
        
        # 计算距离
        pos_distance = self._distance(h_pos, r_pos, t_pos)
        neg_distance = self._distance(h_neg, r_neg, t_neg)
        
        # 计算损失
        loss = torch.mean(F.relu(self.margin + pos_distance - neg_distance))
        
        return loss
    
    def predict(self, h_ids, r_ids, t_ids):
        """
        预测三元组的得分
        Args:
            h_ids: 头实体ID
            r_ids: 关系ID
            t_ids: 尾实体ID
        """
        h_emb = self.entity_embeddings(h_ids)
        r_emb = self.relation_embeddings(r_ids)
        t_emb = self.entity_embeddings(t_ids)
        
        if self.normalize_embeddings:
            h_emb = F.normalize(h_emb, p=2, dim=1)
            t_emb = F.normalize(t_emb, p=2, dim=1)
        
        distance = self._distance(h_emb, r_emb, t_emb)
        return -distance  # 返回负距离作为得分（距离越小，得分越高）
    
    def get_entity_embedding(self, entity_ids):
        """获取实体嵌入"""
        embeddings = self.entity_embeddings(entity_ids)
        if self.normalize_embeddings:
            embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings
    
    def get_relation_embedding(self, relation_ids):
        """获取关系嵌入"""
        return self.relation_embeddings(relation_ids)
    
    def get_all_entity_embeddings(self):
        """获取所有实体嵌入"""
        embeddings = self.entity_embeddings.weight
        if self.normalize_embeddings:
            embeddings = F.normalize(embeddings, p=2, dim=1)
        return embeddings
    
    def get_all_relation_embeddings(self):
        """获取所有关系嵌入"""
        return self.relation_embeddings.weight
    
    def normalize_entity_embeddings(self):
        """归一化所有实体嵌入"""
        with torch.no_grad():
            self.entity_embeddings.weight.data = F.normalize(
                self.entity_embeddings.weight.data, p=2, dim=1
            )
    
    def normalize_relation_embeddings(self):
        """归一化所有关系嵌入"""
        with torch.no_grad():
            self.relation_embeddings.weight.data = F.normalize(
                self.relation_embeddings.weight.data, p=2, dim=1
            )

class TransELoss(nn.Module):
    """TransE损失函数"""
    
    def __init__(self, margin: float = 1.0):
        super(TransELoss, self).__init__()
        self.margin = margin
    
    def forward(self, pos_scores, neg_scores):
        """
        计算TransE损失
        Args:
            pos_scores: 正样本得分
            neg_scores: 负样本得分
        """
        loss = torch.mean(F.relu(self.margin + pos_scores - neg_scores))
        return loss 