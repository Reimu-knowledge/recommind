import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
import logging
from collections import defaultdict
from typing import List, Tuple, Dict, Set
import random

class TripletDataset(Dataset):
    """知识图谱三元组数据集"""
    
    def __init__(self, triplets: List[Tuple[int, int, int]], 
                 entity_to_id: Dict[str, int], 
                 relation_to_id: Dict[str, int],
                 negative_samples: int = 1):
        self.triplets = triplets
        self.entity_to_id = entity_to_id
        self.relation_to_id = relation_to_id
        self.id_to_entity = {v: k for k, v in entity_to_id.items()}
        self.id_to_relation = {v: k for k, v in relation_to_id.items()}
        self.negative_samples = negative_samples
        
        # 构建实体和关系的索引
        self.entity_triplets = defaultdict(list)
        self.relation_triplets = defaultdict(list)
        
        for i, (h, r, t) in enumerate(triplets):
            self.entity_triplets[h].append(i)
            self.entity_triplets[t].append(i)
            self.relation_triplets[r].append(i)
        
        self.entities = list(entity_to_id.keys())
        self.relations = list(relation_to_id.keys())
    
    def __len__(self):
        return len(self.triplets)
    
    def __getitem__(self, idx):
        h, r, t = self.triplets[idx]
        
        # 生成负样本
        negative_triplets = []
        for _ in range(self.negative_samples):
            # 随机选择替换头实体或尾实体
            if random.random() < 0.5:
                # 替换头实体
                neg_h = random.choice(self.entities)
                while neg_h == self.id_to_entity[h]:
                    neg_h = random.choice(self.entities)
                neg_triplet = (self.entity_to_id[neg_h], r, t)
            else:
                # 替换尾实体
                neg_t = random.choice(self.entities)
                while neg_t == self.id_to_entity[t]:
                    neg_t = random.choice(self.entities)
                neg_triplet = (h, r, self.entity_to_id[neg_t])
            negative_triplets.append(neg_triplet)
        
        return {
            'positive': (h, r, t),
            'negative': negative_triplets
        }

class DataManager:
    """知识图谱数据管理器"""
    
    def __init__(self, data_path: str, delimiter: str = ',', header: bool = False,
                 train_ratio: float = 0.8, valid_ratio: float = 0.1, test_ratio: float = 0.1,
                 negative_samples: int = 1):
        self.data_path = data_path
        self.delimiter = delimiter
        self.header = header
        self.train_ratio = train_ratio
        self.valid_ratio = valid_ratio
        self.test_ratio = test_ratio
        self.negative_samples = negative_samples
        
        # 加载和预处理数据
        self._load_data()
        self._build_datasets()
        
        logging.info(f"数据加载完成:")
        logging.info(f"  实体数量: {self.num_entities}")
        logging.info(f"  关系数量: {self.num_relations}")
        logging.info(f"  训练三元组: {len(self.train_triplets)}")
        logging.info(f"  验证三元组: {len(self.valid_triplets)}")
        logging.info(f"  测试三元组: {len(self.test_triplets)}")
    
    def _load_data(self):
        """加载CSV数据文件"""
        logging.info(f"正在加载数据: {self.data_path}")
        
        # 读取CSV文件
        if self.header:
            df = pd.read_csv(self.data_path, delimiter=self.delimiter)
        else:
            df = pd.read_csv(self.data_path, delimiter=self.delimiter, header=None)
            df.columns = ['head', 'relation', 'tail']
        
        # 确保列名正确
        if len(df.columns) != 3:
            raise ValueError(f"CSV文件必须包含3列: head, relation, tail，当前有{len(df.columns)}列")
        
        # 重命名列
        df.columns = ['head', 'relation', 'tail']
        
        # 去除重复和空值
        df = df.dropna().drop_duplicates()
        
        # 构建实体和关系的映射
        all_entities = set(df['head'].unique()) | set(df['tail'].unique())
        all_relations = set(df['relation'].unique())
        
        self.entity_to_id = {entity: idx for idx, entity in enumerate(sorted(all_entities))}
        self.relation_to_id = {relation: idx for idx, relation in enumerate(sorted(all_relations))}
        
        # 转换为ID三元组
        triplets = []
        for _, row in df.iterrows():
            h_id = self.entity_to_id[row['head']]
            r_id = self.relation_to_id[row['relation']]
            t_id = self.entity_to_id[row['tail']]
            triplets.append((h_id, r_id, t_id))
        
        # 随机打乱数据
        random.shuffle(triplets)
        
        # 划分数据集
        total_size = len(triplets)
        train_size = int(total_size * self.train_ratio)
        valid_size = int(total_size * self.valid_ratio)
        
        self.train_triplets = triplets[:train_size]
        self.valid_triplets = triplets[train_size:train_size + valid_size]
        self.test_triplets = triplets[train_size + valid_size:]
        
        # 构建所有三元组的集合（用于过滤评估）
        self.all_triplets = set(triplets)
    
    def _build_datasets(self):
        """构建数据集"""
        self.train_dataset = TripletDataset(
            self.train_triplets, 
            self.entity_to_id, 
            self.relation_to_id,
            self.negative_samples
        )
        
        self.valid_dataset = TripletDataset(
            self.valid_triplets,
            self.entity_to_id,
            self.relation_to_id,
            self.negative_samples
        )
        
        self.test_dataset = TripletDataset(
            self.test_triplets,
            self.entity_to_id,
            self.relation_to_id,
            self.negative_samples
        )
    
    @property
    def num_entities(self):
        return len(self.entity_to_id)
    
    @property
    def num_relations(self):
        return len(self.relation_to_id)
    
    def get_dataloaders(self, batch_size: int, num_workers: int = 4):
        """获取数据加载器"""
        train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            collate_fn=self._collate_fn
        )
        
        valid_loader = DataLoader(
            self.valid_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            collate_fn=self._collate_fn
        )
        
        test_loader = DataLoader(
            self.test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            collate_fn=self._collate_fn
        )
        
        return train_loader, valid_loader, test_loader
    
    def _collate_fn(self, batch):
        """自定义批处理函数"""
        positive_triplets = [item['positive'] for item in batch]
        negative_triplets = [neg for item in batch for neg in item['negative']]
        
        # 转换为张量
        positive_tensor = torch.tensor(positive_triplets, dtype=torch.long)
        negative_tensor = torch.tensor(negative_triplets, dtype=torch.long)
        
        return {
            'positive': positive_tensor,
            'negative': negative_tensor
        }
    
    def get_entity_embeddings(self, model):
        """获取实体嵌入"""
        return model.entity_embeddings.weight.data
    
    def get_relation_embeddings(self, model):
        """获取关系嵌入"""
        return model.relation_embeddings.weight.data
    
    def get_entity_name(self, entity_id: int):
        """根据实体ID获取实体名称"""
        return self.train_dataset.id_to_entity[entity_id]
    
    def get_relation_name(self, relation_id: int):
        """根据关系ID获取关系名称"""
        return self.train_dataset.id_to_relation[relation_id]
    
    def get_entity_id(self, entity_name: str):
        """根据实体名称获取实体ID"""
        return self.entity_to_id[entity_name]
    
    def get_relation_id(self, relation_name: str):
        """根据关系名称获取关系ID"""
        return self.relation_to_id[relation_name] 