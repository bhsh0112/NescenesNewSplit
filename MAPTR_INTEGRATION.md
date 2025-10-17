# MapTR集成指南

本指南说明如何将冗余度划分工具与MapTR集成使用。

## 概述

通过本工具，你可以：
1. 根据数据冗余度筛选NuScenes样本
2. 生成MapTR兼容的数据文件
3. 在MapTR训练中使用低冗余度数据
4. 提高训练效率，减少冗余数据

## 工作流程

```
原始NuScenes数据
    ↓
冗余度分析 (split_by_redundancy.py)
    ↓
冗余度划分结果 (redundancy_split.pkl)
    ↓
MapTR适配 (maptr_adapter.py)
    ↓
MapTR数据文件 (nuscenes_infos_temporal_*.pkl)
    ↓
MapTR训练
```

## 前提条件

### 1. 准备原始MapTR数据

首先需要按照MapTR的标准流程准备数据：

```bash
cd /data2/file_swap/sh_space/map_test/srcs/MapTRv1

# 生成MapTR数据文件
python tools/create_data.py nuscenes \
    --root-path ./data/nuscenes \
    --out-dir ./data/nuscenes \
    --extra-tag nuscenes \
    --version v1.0 \
    --canbus ./data
```

这会生成：
- `data/nuscenes/nuscenes_infos_temporal_train.pkl`
- `data/nuscenes/nuscenes_infos_temporal_val.pkl`

### 2. 运行冗余度分析

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 分析数据冗余度
python split_by_redundancy.py \
    --dataroot /data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes \
    --output-dir ./redundancy_split
```

## 使用方法

### 方式1：仅使用低冗余度数据（推荐）

这是最简单和最常用的方式，只使用低冗余度的数据进行训练：

```bash
python maptr_adapter.py \
    --redundancy-split ./redundancy_split/redundancy_split.pkl \
    --original-train /path/to/nuscenes_infos_temporal_train.pkl \
    --original-val /path/to/nuscenes_infos_temporal_val.pkl \
    --output-dir ./maptr_low_redundancy \
    --mode low_only
```

### 方式2：自定义比例

如果想混合不同冗余度的数据：

```bash
# 70%低冗余度 + 30%中冗余度
python maptr_adapter.py \
    --redundancy-split ./redundancy_split/redundancy_split.pkl \
    --original-train /path/to/nuscenes_infos_temporal_train.pkl \
    --original-val /path/to/nuscenes_infos_temporal_val.pkl \
    --output-dir ./maptr_custom \
    --mode custom \
    --low-ratio 0.7 \
    --medium-ratio 0.3 \
    --high-ratio 0.0
```

### 方式3：平衡各类冗余度

从高、中、低冗余度中各取相同数量的样本：

```bash
python maptr_adapter.py \
    --redundancy-split ./redundancy_split/redundancy_split.pkl \
    --original-train /path/to/nuscenes_infos_temporal_train.pkl \
    --original-val /path/to/nuscenes_infos_temporal_val.pkl \
    --output-dir ./maptr_balanced \
    --mode balanced
```

## 在MapTR中使用

### 方法1：修改配置文件

复制一份MapTR配置文件并修改数据路径：

```python
# projects/configs/maptr/maptr_nano_r18_110e_low_redundancy.py

_base_ = [
    './maptr_nano_r18_110e.py'
]

# 修改数据路径
data_root = '/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/'

data = dict(
    train=dict(
        data_root=data_root,
        ann_file=data_root + 'nuscenes_infos_temporal_train.pkl',
    ),
    val=dict(
        data_root=data_root,
        ann_file=data_root + 'nuscenes_infos_temporal_val.pkl',
    ),
    test=dict(
        data_root=data_root,
        ann_file=data_root + 'nuscenes_infos_temporal_val.pkl',
    )
)
```

### 方法2：使用软链接

```bash
cd /data2/file_swap/sh_space/map_test/srcs/MapTRv1/data/nuscenes

# 备份原始文件
mv nuscenes_infos_temporal_train.pkl nuscenes_infos_temporal_train.pkl.bak
mv nuscenes_infos_temporal_val.pkl nuscenes_infos_temporal_val.pkl.bak

# 创建软链接指向低冗余度数据
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_train.pkl .
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_val.pkl .
```

然后可以直接使用原来的配置文件训练。

## 训练MapTR

```bash
cd /data2/file_swap/sh_space/map_test/srcs/MapTRv1

# 使用修改后的配置文件训练
./tools/dist_train.sh \
    projects/configs/maptr/maptr_nano_r18_110e_low_redundancy.py \
    8 \
    --work-dir work_dirs/maptr_low_redundancy
```

## 完整示例

### 端到端工作流

```bash
# 1. 进入工作目录
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 2. 分析冗余度（如果还没做）
python split_by_redundancy.py

# 3. 生成MapTR低冗余度数据
python maptr_adapter.py \
    --redundancy-split ./redundancy_split/redundancy_split.pkl \
    --original-train ./data/nuscenes/nuscenes_infos_temporal_train.pkl \
    --original-val ./data/nuscenes/nuscenes_infos_temporal_val.pkl \
    --output-dir ./maptr_low_redundancy \
    --mode low_only

# 4. 进入MapTR目录
cd /data2/file_swap/sh_space/map_test/srcs/MapTRv1

# 5. 创建配置文件
cat > projects/configs/maptr/maptr_nano_r18_110e_low_red.py << 'EOF'
_base_ = [
    '../datasets/custom_nus-3d.py',
    '../_base_/default_runtime.py'
]
# ... （复制maptr_nano_r18_110e.py的其他配置）

# 修改数据路径
data = dict(
    train=dict(
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_train.pkl',
    ),
    val=dict(
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_val.pkl',
    ),
)
EOF

# 6. 开始训练
./tools/dist_train.sh \
    projects/configs/maptr/maptr_nano_r18_110e_low_red.py \
    8
```

## 预期效果

使用低冗余度数据训练MapTR可以获得：

1. **训练速度提升**：减少30-50%的训练时间
2. **更好的泛化**：避免过拟合重复场景
3. **资源节省**：减少存储和内存需求
4. **性能保持或提升**：在验证集上保持相似或更好的性能

## 数据统计

运行适配器后，会在输出目录生成 `maptr_split_report.txt`，包含：
- 各冗余度类别的样本数
- 训练集和验证集的样本数
- 总样本数统计

示例：
```
================================================================================
MapTR数据划分报告
================================================================================

包含的冗余度类别:
  - low_redundancy: 8532 samples

训练集样本数: 6144
验证集样本数: 2388
总计: 8532
```

## 比较实验

建议进行对比实验：

| 实验 | 数据 | 样本数 | 训练时间 | mAP |
|------|------|--------|----------|-----|
| Baseline | 全部数据 | 28130 | 100% | XX.X |
| Low Redundancy | 低冗余度 | 8532 | 60% | XX.X |
| Custom | 70%低+30%中 | 12000 | 70% | XX.X |

## 注意事项

1. **数据一致性**：确保冗余度分析和MapTR使用的是同一份NuScenes数据
2. **路径匹配**：适配器生成的pkl文件中的相对路径需要与MapTR的数据根目录匹配
3. **CAN bus数据**：低冗余度划分会保留原始数据中的CAN bus信息
4. **验证集**：验证集也会被过滤，确保训练和验证使用一致的数据分布

## 故障排除

### 问题1：找不到sample token

**错误**：过滤后样本数为0

**原因**：冗余度分析和MapTR数据使用的不是同一份NuScenes

**解决**：确保两者使用相同的数据根目录和版本

### 问题2：路径错误

**错误**：MapTR训练时找不到图像文件

**原因**：pkl文件中的相对路径不匹配

**解决**：检查MapTR配置中的`data_root`设置

### 问题3：性能下降

**现象**：使用低冗余度数据后mAP下降

**可能原因**：
- 某些重要场景被过滤掉
- 数据量太少

**解决**：
- 尝试包含中冗余度数据（`--mode custom --low-ratio 1.0 --medium-ratio 0.5`）
- 调整冗余度阈值重新分析

## Python API使用

在自己的脚本中使用：

```python
from maptr_adapter import MapTRAdapter

# 创建适配器
adapter = MapTRAdapter('redundancy_split.pkl')

# 生成低冗余度数据
result = adapter.create_low_redundancy_split(
    original_train_path='path/to/train.pkl',
    original_val_path='path/to/val.pkl',
    output_dir='./output',
    include_categories=['low_redundancy']
)

print(f"训练集样本数: {result['train_count']}")
print(f"验证集样本数: {result['val_count']}")
```

## 进阶用法

### 1. 组合多个冗余度类别

```python
# 同时包含低冗余度和中冗余度
adapter.create_low_redundancy_split(
    original_train_path='...',
    original_val_path='...',
    output_dir='./output',
    include_categories=['low_redundancy', 'medium_redundancy']
)
```

### 2. 动态采样

```python
from redundancy_utils import RedundancySplitLoader

loader = RedundancySplitLoader('redundancy_split.pkl')

# 采样50%的低冗余度样本
sampled_tokens = loader.sample_from_category(
    'low_redundancy', 
    n=len(loader.get_samples_by_category('low_redundancy')) // 2,
    random_state=42
)

# 使用这些tokens生成MapTR数据
# ...
```

## 总结

通过本集成方案，你可以：
- ✅ 轻松筛选低冗余度数据
- ✅ 生成MapTR兼容的数据文件
- ✅ 提高训练效率
- ✅ 灵活调整数据组成

有任何问题，请参考主README或查看代码注释。

