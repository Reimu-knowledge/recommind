import os
import json
import logging
import time
import torch
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Any
import random

def setup_logging(save_dir: str) -> tuple:
    """设置日志记录"""
    # 创建保存目录（不使用时间戳）
    results_dir = save_dir
    os.makedirs(results_dir, exist_ok=True)
    
    # 设置日志文件
    log_file = os.path.join(results_dir, "experiment.log")
    
    # 获取根日志记录器
    logger = logging.getLogger()
    
    # 清除现有的处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 设置日志级别
    logger.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到根日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # 禁用第三方库的日志
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('torch').setLevel(logging.WARNING)
    logging.getLogger('numpy').setLevel(logging.WARNING)
    
    logging.info(f"日志文件: {log_file}")
    logging.info(f"结果目录: {results_dir}")
    
    return results_dir, log_file

def set_random_seed(seed: int):
    """设置随机种子"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    
    logging.info(f"随机种子设置为: {seed}")

def save_experiment_config(args, save_dir: str):
    """保存实验配置"""
    config_file = os.path.join(save_dir, "experiment_config.json")
    
    # 将args转换为字典
    config = {}
    for key, value in vars(args).items():
        if isinstance(value, (int, float, str, bool, list)):
            config[key] = value
        else:
            config[key] = str(value)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logging.info(f"实验配置已保存到: {config_file}")

def save_results_summary(results: Dict[str, Any], save_dir: str):
    """保存结果摘要"""
    results_file = os.path.join(save_dir, "results_summary.json")
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logging.info(f"结果摘要已保存到: {results_file}")

def plot_training_curves(training_history: Dict[str, List[float]], save_dir: str):
    """绘制训练曲线"""
    epochs = range(1, len(training_history['train_loss']) + 1)
    
    # 创建子图
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('TransE Training Curves', fontsize=16)
    
    # 训练损失
    axes[0, 0].plot(epochs, training_history['train_loss'], 'b-', label='Train Loss')
    axes[0, 0].set_title('Training Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # 验证损失
    axes[0, 1].plot(epochs, training_history['valid_loss'], 'r-', label='Valid Loss')
    axes[0, 1].set_title('Validation Loss')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Loss')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # MRR
    if 'valid_mrr' in training_history:
        axes[1, 0].plot(epochs, training_history['valid_mrr'], 'g-', label='Valid MRR')
        axes[1, 0].set_title('Mean Reciprocal Rank')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('MRR')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
    
    # Hits@10
    if 'valid_hits_at_10' in training_history:
        axes[1, 1].plot(epochs, training_history['valid_hits_at_10'], 'm-', label='Valid Hits@10')
        axes[1, 1].set_title('Hits@10')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Hits@10')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
    
    plt.tight_layout()
    
    # 保存图片
    plot_file = os.path.join(save_dir, "training_curves.png")
    plt.savefig(plot_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    logging.info(f"训练曲线已保存到: {plot_file}")

def save_embeddings(model, data_manager, save_dir: str):
    """保存实体和关系嵌入"""
    # 保存实体嵌入
    entity_embeddings = model.get_all_entity_embeddings().detach().cpu().numpy()
    entity_file = os.path.join(save_dir, "entity_embeddings.npy")
    np.save(entity_file, entity_embeddings)
    
    # 保存关系嵌入
    relation_embeddings = model.get_all_relation_embeddings().detach().cpu().numpy()
    relation_file = os.path.join(save_dir, "relation_embeddings.npy")
    np.save(relation_file, relation_embeddings)
    
    # 保存映射信息
    mapping_file = os.path.join(save_dir, "entity_relation_mapping.json")
    mapping = {
        'entity_to_id': data_manager.entity_to_id,
        'relation_to_id': data_manager.relation_to_id,
        'id_to_entity': {v: k for k, v in data_manager.entity_to_id.items()},
        'id_to_relation': {v: k for k, v in data_manager.relation_to_id.items()}
    }
    
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    logging.info(f"嵌入已保存到: {save_dir}")
    logging.info(f"  实体嵌入: {entity_file}")
    logging.info(f"  关系嵌入: {relation_file}")
    logging.info(f"  映射信息: {mapping_file}")

def print_experiment_summary(args):
    """打印实验摘要"""
    logging.info("=" * 60)
    logging.info("TransE 知识图谱嵌入实验")
    logging.info("=" * 60)
    logging.info(f"数据路径: {args.data_path}")
    logging.info(f"嵌入维度: {args.embedding_dim}")
    logging.info(f"距离度量: {args.distance_metric}")
    logging.info(f"Margin: {args.margin}")
    logging.info(f"学习率: {args.learning_rate}")
    logging.info(f"批次大小: {args.batch_size}")
    logging.info(f"训练轮数: {args.epochs}")
    logging.info(f"负样本数量: {args.negative_samples}")
    logging.info(f"设备: {'GPU' if args.gpu >= 0 else 'CPU'}")
    if args.gpu >= 0:
        logging.info(f"GPU ID: {args.gpu}")
    logging.info("=" * 60)

def count_parameters(model) -> int:
    """计算模型参数数量"""
    return sum(p.numel() for p in model.parameters())

def format_time(seconds: float) -> str:
    """格式化时间"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{int(minutes)}m {seconds:.2f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{int(hours)}h {int(minutes)}m {seconds:.2f}s"

def create_sample_data(save_path: str, num_entities: int = 100, num_relations: int = 10, num_triplets: int = 1000):
    """创建示例数据用于测试"""
    import pandas as pd
    
    # 生成实体和关系
    entities = [f"entity_{i}" for i in range(num_entities)]
    relations = [f"relation_{i}" for i in range(num_relations)]
    
    # 生成三元组
    triplets = []
    for _ in range(num_triplets):
        h = random.choice(entities)
        r = random.choice(relations)
        t = random.choice(entities)
        triplets.append([h, r, t])
    
    # 去除重复
    triplets = list(set(map(tuple, triplets)))
    
    # 保存为CSV
    df = pd.DataFrame(triplets, columns=['head', 'relation', 'tail'])
    df.to_csv(save_path, index=False, header=False)
    
    logging.info(f"示例数据已创建: {save_path}")
    logging.info(f"  实体数量: {len(set(df['head'].unique()) | set(df['tail'].unique()))}")
    logging.info(f"  关系数量: {len(df['relation'].unique())}")
    logging.info(f"  三元组数量: {len(df)}")

def load_embeddings(embedding_file: str, mapping_file: str):
    """加载保存的嵌入"""
    # 加载嵌入
    embeddings = np.load(embedding_file)
    
    # 加载映射
    with open(mapping_file, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    return embeddings, mapping 