# MapTR使用生成数据的说明

## ❌ 不能直接使用

**`maptr_balanced/` 文件夹不能直接作为 `data_root` 使用！**

原因：
- `maptr_balanced/` 只包含**索引文件**（pkl），不包含实际数据
- pkl文件中存储的路径是相对路径（如 `./data/samples/CAM_FRONT/...`）
- 实际的图像、点云等数据还在原始nuscenes目录中

## ✅ 正确的使用方法

### 方法1：修改MapTR配置文件（推荐）

在MapTR配置文件中：

```python
# projects/configs/maptr/your_config.py

# data_root 仍然指向原始nuscenes目录
data_root = 'data/nuscenes/'

# 只修改ann_file指向新生成的pkl文件
data = dict(
    samples_per_gpu=4,
    workers_per_gpu=4,
    train=dict(
        type='NuScenesDataset',
        data_root=data_root,  # 原始数据目录
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl',  # 新生成的索引
        pipeline=train_pipeline,
        ...
    ),
    val=dict(
        type='NuScenesDataset',
        data_root=data_root,  # 原始数据目录
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_val.pkl',  # 新生成的索引
        pipeline=test_pipeline,
        ...
    ),
)
```

### 方法2：使用软链接（简单）

如果你想保持配置文件不变，可以替换原始的pkl文件：

```bash
cd /path/to/MapTR/data/nuscenes

# 1. 备份原始文件
mv nuscenes_infos_temporal_train.pkl nuscenes_infos_temporal_train.pkl.original
mv nuscenes_infos_temporal_val.pkl nuscenes_infos_temporal_val.pkl.original

# 2. 创建软链接
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl .
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_val.pkl .
```

## 📊 生成的数据统计

让我检查一下你的平衡数据集：

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit
cat maptr_balanced/maptr_split_report.txt
```

## 🔍 验证数据

验证pkl文件是否正确生成：

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

python3 << 'EOF'
import pickle

with open('maptr_balanced/nuscenes_infos_temporal_train.pkl', 'rb') as f:
    train_data = pickle.load(f)

with open('maptr_balanced/nuscenes_infos_temporal_val.pkl', 'rb') as f:
    val_data = pickle.load(f)

print(f"训练集: {len(train_data['infos'])} samples")
print(f"验证集: {len(val_data['infos'])} samples")
print(f"总计: {len(train_data['infos']) + len(val_data['infos'])} samples")
EOF
```

## 📁 完整的MapTR数据结构

MapTR实际需要的完整结构：

```
MapTR/
└── data/
    └── nuscenes/
        ├── samples/              ← 实际图像数据
        ├── sweeps/               ← 实际点云数据
        ├── maps/                 ← 地图数据
        ├── v1.0-trainval/        ← 元数据
        ├── nuscenes_infos_temporal_train.pkl  ← 索引文件（指向上面的数据）
        └── nuscenes_infos_temporal_val.pkl    ← 索引文件
```

你生成的pkl文件只是**索引文件**，它告诉MapTR：
- 使用哪些samples
- 这些samples的文件路径在哪里
- 相关的标注信息

但实际数据（图像、点云等）还在原始nuscenes目录中。

## 🎯 总结

| 项目 | 说明 |
|------|------|
| **data_root** | 必须指向包含`samples/`, `sweeps/`等实际数据的目录 |
| **ann_file** | 指向生成的pkl索引文件 |
| **maptr_balanced/** | 只包含索引文件，不能作为data_root |

## ⚠️ 常见错误

### 错误1：将maptr_balanced作为data_root
```python
# ❌ 错误
data_root = '/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/'
```
**结果**：找不到图像文件

### 错误2：路径不匹配
```python
# ❌ 错误
data_root = '/different/path/to/nuscenes'  # 与pkl中的路径不匹配
```
**结果**：路径错误

## ✅ 正确示例

```python
# ✓ 正确
data_root = 'data/nuscenes/'  # 或你的nuscenes实际路径
ann_file = '/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl'
```

## 🚀 开始训练

配置好后，正常运行MapTR训练：

```bash
cd /path/to/MapTR

# 训练
./tools/dist_train.sh \
    projects/configs/maptr/your_config.py \
    8 \
    --work-dir work_dirs/maptr_balanced
```

## 📝 需要注意

1. **data_root**：指向原始nuscenes数据（包含samples/, sweeps/等）
2. **ann_file**：指向新生成的pkl文件
3. pkl文件中的路径是相对于某个基准目录的，确保MapTR能找到

## 🔧 如果遇到路径问题

如果训练时找不到文件，检查：

1. pkl文件中的路径格式：
```python
import pickle
with open('maptr_balanced/nuscenes_infos_temporal_train.pkl', 'rb') as f:
    data = pickle.load(f)
    print(data['infos'][0]['cams']['CAM_FRONT']['data_path'])
```

2. 确保这个路径相对于data_root是正确的

3. 如果路径有问题，可能需要重新生成pkl文件

