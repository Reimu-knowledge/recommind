# TransE 知识图谱嵌入

基于论文《Translating Embeddings for Modeling Multi-relational Data》的TransE模型实现。

## 项目简介

TransE是一种用于知识图谱嵌入的方法，它将关系建模为实体嵌入空间中的翻译操作。该方法简单而有效，在链接预测任务上取得了优异的性能。

## 核心思想

TransE的核心假设是：如果三元组 (h, r, t) 成立，那么尾实体 t 的嵌入应该接近头实体 h 的嵌入加上关系 r 的嵌入，即：

```
h + r ≈ t
```

## 项目结构

```
transE/
├── main.py              # 主程序入口
├── args.py              # 参数配置
├── data_manager.py      # 数据管理
├── model.py             # TransE模型实现
├── train.py             # 训练模块
├── evaluate.py          # 评估模块
├── utils.py             # 工具函数
├── requirements.txt     # 依赖包
└── README.md           # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 准备数据

数据格式为CSV文件，每行包含一个三元组：`head,relation,tail`

示例：
```
entity_1,relation_1,entity_2
entity_2,relation_2,entity_3
...
```

### 2. 运行训练

```bash
python main.py --data_path your_data.csv --embedding_dim 50 --epochs 1000
```

### 3. 主要参数说明

- `--data_path`: 数据文件路径（必需）
- `--embedding_dim`: 嵌入维度（默认50）
- `--margin`: 损失函数中的margin参数（默认1.0）
- `--distance_metric`: 距离度量方法，L1或L2（默认L1）
- `--learning_rate`: 学习率（默认0.01）
- `--batch_size`: 批次大小（默认1024）
- `--epochs`: 训练轮数（默认1000）
- `--gpu`: GPU设备ID，-1表示使用CPU（默认0）

### 4. 完整示例

```bash
python main.py \
    --data_path data/knowledge_graph.csv \
    --embedding_dim 100 \
    --margin 1.0 \
    --distance_metric L1 \
    --learning_rate 0.01 \
    --batch_size 1024 \
    --epochs 1000 \
    --gpu 0 \
    --filtered_eval \
    --save_dir ./results
```

## 输出结果

训练完成后，会在结果目录中生成以下文件：

- `experiment.log`: 训练日志
- `experiment_config.json`: 实验配置
- `results_summary.json`: 结果摘要
- `training_curves.png`: 训练曲线图
- `best_model.pth`: 最佳模型
- `entity_embeddings.npy`: 实体嵌入
- `relation_embeddings.npy`: 关系嵌入
- `entity_relation_mapping.json`: 实体和关系映射
- `sample_predictions.json`: 示例预测结果

## 评估指标

- **MRR (Mean Reciprocal Rank)**: 平均倒数排名
- **Hits@K**: 排名在前K位的比例
- **Mean Rank**: 平均排名
- **Median Rank**: 中位数排名

## 模型特点

1. **简单有效**: 模型结构简单，参数少，训练效率高
2. **可扩展**: 能够处理大规模知识图谱
3. **理论基础**: 基于翻译假设，符合知识图谱的层次结构
4. **性能优异**: 在多个基准数据集上表现优秀

## 论文引用

```
@inproceedings{bordes2013translating,
  title={Translating embeddings for modeling multi-relational data},
  author={Bordes, Antoine and Usunier, Nicolas and Garcia-Duran, Alberto and Weston, Jason and Yakhnenko, Oksana},
  booktitle={Advances in neural information processing systems},
  pages={2787--2795},
  year={2013}
}
```

## 注意事项

1. 确保数据文件格式正确，包含三列：head, relation, tail
2. 对于大规模数据集，建议使用GPU加速训练
3. 可以通过调整margin和距离度量来优化性能
4. 使用过滤评估可以获得更准确的性能评估

## 扩展功能

- 支持多种距离度量（L1, L2）
- 支持过滤评估和原始评估
- 提供完整的训练曲线可视化
- 支持模型保存和加载
- 提供示例预测功能

## 许可证

本项目采用MIT许可证。 