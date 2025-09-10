import argparse
import os

def get_args():
    parser = argparse.ArgumentParser(description='TransE Knowledge Graph Embedding')
    
    # 数据相关参数
    parser.add_argument('--data_path', type=str, required=True, help='知识图谱三元组数据文件路径(.csv)')
    parser.add_argument('--delimiter', type=str, default=',', help='CSV文件分隔符')
    parser.add_argument('--header', action='store_true', help='CSV文件是否包含表头')
    parser.add_argument('--train_ratio', type=float, default=0.8, help='训练集比例')
    parser.add_argument('--valid_ratio', type=float, default=0.1, help='验证集比例')
    parser.add_argument('--test_ratio', type=float, default=0.1, help='测试集比例')
    
    # 模型参数
    parser.add_argument('--embedding_dim', type=int, default=50, help='实体和关系的嵌入维度')
    parser.add_argument('--margin', type=float, default=1.0, help='损失函数中的margin参数')
    parser.add_argument('--distance_metric', type=str, default='L1', choices=['L1', 'L2'], help='距离度量方法')
    parser.add_argument('--normalize_embeddings', action='store_true', help='是否对实体嵌入进行L2归一化')
    
    # 训练参数
    parser.add_argument('--batch_size', type=int, default=1024, help='批次大小')
    parser.add_argument('--epochs', type=int, default=1000, help='训练轮数')
    parser.add_argument('--learning_rate', type=float, default=0.01, help='学习率')
    parser.add_argument('--negative_samples', type=int, default=1, help='每个正样本对应的负样本数量')
    parser.add_argument('--early_stopping_patience', type=int, default=10, help='早停耐心值')
    parser.add_argument('--early_stopping_delta', type=float, default=0.001, help='早停改善阈值')
    
    # 评估参数
    parser.add_argument('--eval_batch_size', type=int, default=1024, help='评估批次大小')
    parser.add_argument('--filtered_eval', action='store_true', help='是否使用过滤评估')
    parser.add_argument('--hits_at_k', type=int, nargs='+', default=[1, 3, 10], help='Hits@K评估的K值')
    
    # 系统参数
    parser.add_argument('--seed', type=int, default=42, help='随机种子')
    parser.add_argument('--num_workers', type=int, default=4, help='数据加载器工作进程数')
    parser.add_argument('--gpu', type=int, default=0, help='GPU设备ID，-1表示使用CPU')
    parser.add_argument('--save_dir', type=str, default='./results', help='结果保存目录')
    parser.add_argument('--model_name', type=str, default='transe', help='模型名称')
    
    # 日志参数
    parser.add_argument('--log_interval', type=int, default=100, help='日志记录间隔')
    parser.add_argument('--eval_interval', type=int, default=1000, help='评估间隔')
    parser.add_argument('--save_interval', type=int, default=5000, help='模型保存间隔')
    
    args = parser.parse_args()
    
    # 验证参数
    assert 0 < args.train_ratio < 1, "训练集比例必须在(0,1)之间"
    assert 0 < args.valid_ratio < 1, "验证集比例必须在(0,1)之间"
    assert 0 < args.test_ratio < 1, "测试集比例必须在(0,1)之间"
    assert abs(args.train_ratio + args.valid_ratio + args.test_ratio - 1.0) < 1e-6, "数据集比例之和必须为1"
    
    # 创建保存目录
    os.makedirs(args.save_dir, exist_ok=True)
    
    return args 