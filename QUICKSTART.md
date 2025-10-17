# 快速开始指南

## 1. 安装依赖

```bash
pip install -r requirements.txt
```

## 2. 运行完整流程（最简单）

使用提供的一键运行脚本：

```bash
./run_example.sh
```

这将自动完成数据划分和可视化。

## 3. 分步运行

### 步骤1：数据划分

```bash
python split_by_redundancy.py
```

默认参数：
- 数据路径: `/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes`
- 低速阈值: 1.0 m/s
- 高速阈值: 5.0 m/s
- 输出目录: `./redundancy_split`

### 步骤2：可视化结果

```bash
python visualize_redundancy.py
```

### 步骤3：使用划分结果

```bash
python usage_example.py
```

## 4. 自定义参数

如果需要调整参数：

```bash
python split_by_redundancy.py \
    --dataroot /your/nuscenes/path \
    --low-velocity 0.5 \
    --high-velocity 8.0 \
    --high-redundancy-threshold 0.7 \
    --low-redundancy-threshold 0.2
```

## 5. 在代码中使用

```python
from redundancy_utils import RedundancySplitLoader

# 加载划分结果
loader = RedundancySplitLoader('./redundancy_split/redundancy_split.pkl')

# 获取低冗余度样本
low_samples = loader.get_samples_by_category('low_redundancy')

# 创建训练/验证/测试划分
split = loader.get_balanced_split(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
train_samples = split['train']
```

## 6. 输出文件说明

运行后会在输出目录生成以下文件：

### 数据文件
- `redundancy_split.pkl` - 划分结果（Python pickle）
- `redundancy_split.json` - 划分结果（JSON格式）
- `*_sample_tokens.txt` - 各类别的样本token列表

### 报告和图表
- `redundancy_report.txt` - 详细统计报告
- `redundancy_distribution.png` - 分布图
- `velocity_histogram.png` - 速率直方图
- `redundancy_scatter.png` - 散点图
- `redundancy_pie_charts.png` - 饼图

## 7. 常见问题

**Q: 如何只使用低冗余度数据训练？**

```python
loader = RedundancySplitLoader('redundancy_split.pkl')
low_samples = loader.get_samples_by_category('low_redundancy')
# 使用 low_samples 进行训练
```

**Q: 如何调整参数使低冗余度样本更多？**

- 增加 `--high-velocity` 值
- 降低 `--low-redundancy-threshold` 值

**Q: 数据已经存在train/val划分，如何使用这个工具？**

可以先用这个工具分析冗余度，然后筛选出低冗余度的样本，再与现有划分结合使用。

## 8. 性能建议

- 完整数据集分析约需 2-5 分钟
- 使用低冗余度子集可减少训练时间 30-50%
- 建议先在小数据集上验证效果

## 9. 更多信息

详细文档请查看 `README.md`

