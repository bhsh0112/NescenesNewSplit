# NuScenes数据集冗余度划分工具

本工具用于基于数据冗余度对NuScenes数据集进行新的划分。冗余度通过车辆位移速率判断：速率较低时持续采集同一场景的数据，冗余度高；反之冗余度低。

## 功能特点

- **冗余度分析**：基于ego vehicle的位移速率计算数据冗余度
- **自动划分**：将数据分为高、中、低冗余度三类
- **结果保存**：支持多种格式（pickle、JSON、txt）
- **可视化**：生成多种统计图表帮助理解数据分布
- **统计报告**：生成详细的文本统计报告

## 安装依赖

```bash
pip install numpy matplotlib
```

## 使用方法

### 1. 数据划分

运行主脚本对数据集进行划分：

```bash
python split_by_redundancy.py \
    --dataroot /path/to/nuscenes \
    --version v1.0-trainval \
    --output-dir ./redundancy_split \
    --low-velocity 1.0 \
    --high-velocity 5.0 \
    --high-redundancy-threshold 0.6 \
    --low-redundancy-threshold 0.3
```

**参数说明**：

- `--dataroot`: NuScenes数据集根目录
- `--version`: 数据集版本（默认：v1.0-trainval）
- `--output-dir`: 输出目录
- `--low-velocity`: 低速阈值（米/秒），低于此速度认为冗余度高（默认：1.0）
- `--high-velocity`: 高速阈值（米/秒），高于此速度认为冗余度低（默认：5.0）
- `--high-redundancy-threshold`: 高冗余度分类阈值（默认：0.6）
- `--low-redundancy-threshold`: 低冗余度分类阈值（默认：0.3）

### 2. 可视化结果

运行可视化脚本生成图表：

```bash
python visualize_redundancy.py \
    --result-path ./redundancy_split/redundancy_split.pkl \
    --output-dir ./redundancy_split
```

**参数说明**：

- `--result-path`: 划分结果文件路径（.pkl或.json）
- `--output-dir`: 可视化结果输出目录

## 输出文件

运行后会在输出目录生成以下文件：

### 数据文件

- `redundancy_split.pkl`: 划分结果（pickle格式）
- `redundancy_split.json`: 划分结果（JSON格式）
- `high_redundancy_sample_tokens.txt`: 高冗余度样本的token列表
- `medium_redundancy_sample_tokens.txt`: 中冗余度样本的token列表
- `low_redundancy_sample_tokens.txt`: 低冗余度样本的token列表

### 报告和可视化

- `redundancy_report.txt`: 详细统计报告
- `redundancy_distribution.png`: 冗余度分布图
- `velocity_histogram.png`: 速率分布直方图
- `redundancy_scatter.png`: 速率-冗余度散点图
- `redundancy_pie_charts.png`: 数据占比饼图

## 工作原理

### 冗余度计算

1. **位移速率计算**：
   - 对于每个scene中的连续samples，计算ego vehicle的位移距离
   - 速率 = 位移距离 / 时间差

2. **冗余度评分**：
   - 速率 ≤ 低速阈值：冗余度 = 1.0（最高）
   - 速率 ≥ 高速阈值：冗余度 = 0.0（最低）
   - 中间速率：线性插值计算冗余度

3. **场景分类**：
   - 计算每个scene的平均冗余度
   - 根据阈值分为高、中、低三类

### 数据结构

划分结果的数据结构：

```python
{
    'high_redundancy': [
        {
            'scene_token': 'xxx',
            'scene_name': 'scene-0001',
            'sample_tokens': ['token1', 'token2', ...],
            'avg_velocity': 0.5,
            'avg_redundancy': 0.85,
            'num_samples': 40
        },
        ...
    ],
    'medium_redundancy': [...],
    'low_redundancy': [...]
}
```

## 使用示例

### 示例1：使用默认参数

```bash
# 数据划分
python split_by_redundancy.py

# 可视化
python visualize_redundancy.py
```

### 示例2：自定义参数

```bash
# 更严格的冗余度判定
python split_by_redundancy.py \
    --low-velocity 0.5 \
    --high-velocity 8.0 \
    --high-redundancy-threshold 0.7 \
    --low-redundancy-threshold 0.2
```

### 示例3：Python API使用

```python
from split_by_redundancy import NuScenesRedundancySplitter

# 初始化
splitter = NuScenesRedundancySplitter(
    dataroot='/path/to/nuscenes',
    version='v1.0-trainval'
)

# 分析所有scenes
analysis_results = splitter.analyze_all_scenes(
    low_threshold=1.0,
    high_threshold=5.0
)

# 进行划分
split_result = splitter.split_by_redundancy(
    analysis_results,
    high_redundancy_threshold=0.6,
    low_redundancy_threshold=0.3
)

# 保存结果
splitter.save_split(split_result, './output')

# 访问特定类别的数据
high_redundancy_scenes = split_result['high_redundancy']
for scene in high_redundancy_scenes:
    print(f"Scene: {scene['scene_name']}, "
          f"Velocity: {scene['avg_velocity']:.2f} m/s")
```

## 应用场景

这个工具可以用于：

1. **数据采样**：从低冗余度数据中选择更具代表性的训练样本
2. **数据增强**：识别高冗余度场景，减少重复训练
3. **效率优化**：优先处理低冗余度数据，提高训练效率
4. **数据分析**：理解数据集中不同场景的分布特征

## 注意事项

- 确保NuScenes数据集已正确下载和解压
- 脚本需要读取`ego_pose.json`、`sample.json`等元数据文件
- 可视化需要安装matplotlib
- 处理完整数据集可能需要几分钟时间

## 参数调优建议

- **低速阈值**（0.5-2.0 m/s）：
  - 较低值：更严格地定义高冗余度
  - 较高值：更宽松地定义高冗余度

- **高速阈值**（3.0-10.0 m/s）：
  - 较低值：更多场景被归类为低冗余度
  - 较高值：更严格地定义低冗余度

- **分类阈值**：
  - 根据实际需求调整高、中、低的比例
  - 建议先运行一次查看分布，再调整阈值

## 许可证

本工具遵循与NuScenes数据集相同的许可证要求。

## 联系方式

如有问题或建议，请联系开发者。

