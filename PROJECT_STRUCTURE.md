# 项目结构说明

```
nuscenes_NewSplit/
│
├── data/                           # 数据目录
│   └── nuscenes/                   # NuScenes数据集
│       ├── v1.0-trainval/          # 元数据文件
│       ├── samples/                # 关键帧数据
│       └── sweeps/                 # 中间帧数据
│
├── split_by_redundancy.py          # 主程序：数据划分
├── visualize_redundancy.py         # 可视化工具
├── redundancy_utils.py             # 工具类：加载和使用划分结果
├── usage_example.py                # 使用示例
│
├── run_example.sh                  # 一键运行脚本
├── requirements.txt                # Python依赖
│
├── README.md                       # 详细文档
├── QUICKSTART.md                   # 快速开始指南
└── PROJECT_STRUCTURE.md            # 本文件
```

## 核心文件说明

### 1. split_by_redundancy.py
**核心功能模块**

- `NuScenesRedundancySplitter` 类：主要的数据划分器
  - `__init__()`: 加载NuScenes数据集
  - `calculate_velocity()`: 计算两个sample之间的速率
  - `calculate_redundancy_score()`: 根据速率计算冗余度分数
  - `analyze_scene()`: 分析单个场景
  - `analyze_all_scenes()`: 分析所有场景
  - `split_by_redundancy()`: 根据冗余度划分数据
  - `save_split()`: 保存划分结果

**命令行参数**:
- `--dataroot`: 数据集路径
- `--version`: 数据集版本
- `--output-dir`: 输出目录
- `--low-velocity`: 低速阈值
- `--high-velocity`: 高速阈值
- `--high-redundancy-threshold`: 高冗余度阈值
- `--low-redundancy-threshold`: 低冗余度阈值

### 2. visualize_redundancy.py
**可视化工具**

生成的图表：
- `redundancy_distribution.png`: 四宫格分布图
- `velocity_histogram.png`: 速率直方图
- `redundancy_scatter.png`: 速率-冗余度散点图
- `redundancy_pie_charts.png`: 占比饼图

函数：
- `plot_redundancy_distribution()`: 绘制综合分布图
- `plot_velocity_histogram()`: 绘制速率直方图
- `plot_redundancy_scatter()`: 绘制散点图
- `plot_pie_charts()`: 绘制饼图
- `print_statistics()`: 打印统计信息

### 3. redundancy_utils.py
**工具类库**

- `RedundancySplitLoader` 类：划分结果加载器
  - `get_category_by_sample()`: 查询样本类别
  - `get_category_by_scene()`: 查询场景类别
  - `get_samples_by_category()`: 获取指定类别的样本
  - `sample_from_category()`: 从类别中随机采样
  - `get_balanced_split()`: 创建平衡划分
  - `get_low_redundancy_subset()`: 获取低冗余度子集
  - `get_statistics()`: 获取统计信息
  - `print_summary()`: 打印摘要

### 4. usage_example.py
**6个使用示例**

1. 基本使用
2. 样本筛选
3. 平衡划分
4. 查询样本
5. 场景分析
6. 自定义训练策略

### 5. run_example.sh
**一键运行脚本**

自动执行：
1. 检查数据集
2. 运行数据划分
3. 生成可视化
4. 显示结果路径

## 工作流程

```
1. 加载NuScenes数据集
         ↓
2. 分析每个scene的ego pose
         ↓
3. 计算连续samples之间的速率
         ↓
4. 根据速率计算冗余度分数
         ↓
5. 按冗余度阈值划分为三类
         ↓
6. 保存结果和生成报告
         ↓
7. 可视化分析结果
         ↓
8. 在训练中使用划分结果
```

## 数据流

```
NuScenes数据集
    ├── ego_pose.json      → 车辆位姿信息
    ├── sample.json        → 关键帧信息
    ├── sample_data.json   → 传感器数据
    └── scene.json         → 场景信息
         ↓
    分析处理
         ↓
    划分结果
    ├── redundancy_split.pkl
    ├── redundancy_split.json
    └── *_sample_tokens.txt
         ↓
    应用
    ├── 训练集筛选
    ├── 数据增强
    └── 效率优化
```

## 输出目录结构

```
redundancy_split/
├── redundancy_split.pkl                    # 划分结果（pickle）
├── redundancy_split.json                   # 划分结果（JSON）
├── redundancy_report.txt                   # 统计报告
│
├── high_redundancy_sample_tokens.txt       # 高冗余度样本列表
├── medium_redundancy_sample_tokens.txt     # 中冗余度样本列表
├── low_redundancy_sample_tokens.txt        # 低冗余度样本列表
│
├── redundancy_distribution.png             # 分布图
├── velocity_histogram.png                  # 直方图
├── redundancy_scatter.png                  # 散点图
└── redundancy_pie_charts.png              # 饼图
```

## 核心算法

### 速率计算
```python
位移距离 = ||pos2 - pos1||
时间差 = (timestamp2 - timestamp1) / 1e6
速率 = 位移距离 / 时间差
```

### 冗余度评分
```python
if 速率 <= 低速阈值:
    冗余度 = 1.0
elif 速率 >= 高速阈值:
    冗余度 = 0.0
else:
    冗余度 = 1.0 - (速率 - 低速阈值) / (高速阈值 - 低速阈值)
```

### 场景分类
```python
场景平均冗余度 = mean(所有samples的冗余度)

if 平均冗余度 >= 高冗余度阈值:
    类别 = 'high_redundancy'
elif 平均冗余度 <= 低冗余度阈值:
    类别 = 'low_redundancy'
else:
    类别 = 'medium_redundancy'
```

## 扩展性

### 添加新的分析指标
可以在 `NuScenesRedundancySplitter` 类中添加新的分析方法：
```python
def calculate_new_metric(self, sample_token):
    # 自定义分析逻辑
    pass
```

### 自定义可视化
可以在 `visualize_redundancy.py` 中添加新的绘图函数：
```python
def plot_custom_analysis(split_result, output_dir):
    # 自定义可视化逻辑
    pass
```

### 集成到现有流程
使用 `RedundancySplitLoader` 类可以轻松集成到现有的训练流程：
```python
from redundancy_utils import RedundancySplitLoader

loader = RedundancySplitLoader('path/to/result.pkl')
filtered_samples = loader.get_samples_by_category('low_redundancy')
# 使用 filtered_samples 进行训练
```

## 依赖关系

```
split_by_redundancy.py
    └── 依赖: numpy

visualize_redundancy.py
    └── 依赖: numpy, matplotlib

redundancy_utils.py
    └── 依赖: numpy

usage_example.py
    └── 依赖: redundancy_utils.py
```

## 性能指标

- 数据加载时间: ~5-10秒
- 分析时间: ~2-5分钟（全量数据集）
- 可视化时间: ~5-10秒
- 内存占用: ~500MB-1GB

## 适用场景

1. **减少训练数据冗余**
   - 筛选出低冗余度数据
   - 提高训练效率

2. **数据集质量分析**
   - 了解数据分布
   - 识别问题场景

3. **采样策略优化**
   - 智能采样
   - 平衡数据分布

4. **效率提升**
   - 减少重复数据
   - 加快实验迭代

