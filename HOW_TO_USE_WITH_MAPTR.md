# 如何在MapTR中使用生成的数据

## 🎯 快速回答

**❌ `maptr_balanced/` 不能直接作为 `data_root` 使用！**

**✅ 正确方法：保持 `data_root` 指向原始nuscenes，只修改 `ann_file`**

---

## 📊 你的数据集统计

根据 `maptr_balanced/` 的内容：
- **训练集**: 17,513 samples
- **验证集**: 3,709 samples  
- **总计**: 21,222 samples（原始数据集的62%）

这是从高、中、低三个冗余度类别中**各取7,074个样本**的平衡子集。

---

## 📁 文件结构说明

### 当前目录结构

```
nuscenes_NewSplit/
├── data/
│   └── nuscenes/                    ← 原始NuScenes数据
│       ├── samples/                 ← 实际图像文件
│       ├── sweeps/                  ← 实际点云文件
│       ├── maps/                    ← 地图文件
│       └── v1.0-trainval/          ← 元数据
│
└── maptr_balanced/                  ← 你生成的文件夹
    ├── nuscenes_infos_temporal_train.pkl   ← 训练集索引
    ├── nuscenes_infos_temporal_val.pkl     ← 验证集索引
    └── maptr_split_report.txt              ← 统计报告
```

### 关键理解

- **`maptr_balanced/`** 只包含**索引文件**（pkl）
- **索引文件**记录：使用哪些samples、文件路径、标注信息
- **实际数据**（图像、点云等）仍在 `data/nuscenes/` 中
- pkl文件中的路径是**相对路径**，如：`./data/samples/CAM_FRONT/xxx.jpg`

---

## ✅ 方法1：修改MapTR配置文件（推荐）

### 步骤1：创建新配置文件

```bash
cd /path/to/MapTR
cp projects/configs/maptr/maptr_nano_r18_110e.py \
   projects/configs/maptr/maptr_nano_r18_110e_balanced.py
```

### 步骤2：修改配置

编辑 `maptr_nano_r18_110e_balanced.py`：

```python
_base_ = [
    '../datasets/custom_nus-3d.py',
    '../_base_/default_runtime.py'
]

# 其他配置保持不变...

# 只修改数据配置部分
data = dict(
    samples_per_gpu=4,
    workers_per_gpu=4,
    train=dict(
        type='NuScenesDataset',
        data_root='data/nuscenes/',  # 仍然指向原始数据目录
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl',
        # 其他参数...
    ),
    val=dict(
        type='NuScenesDataset',
        data_root='data/nuscenes/',
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_val.pkl',
        # 其他参数...
    ),
    test=dict(
        type='NuScenesDataset',
        data_root='data/nuscenes/',
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_val.pkl',
        # 其他参数...
    ),
)
```

### 步骤3：训练

```bash
cd /path/to/MapTR

./tools/dist_train.sh \
    projects/configs/maptr/maptr_nano_r18_110e_balanced.py \
    8 \
    --work-dir work_dirs/maptr_balanced
```

---

## ✅ 方法2：使用软链接（更简单）

如果不想修改配置文件：

```bash
cd /path/to/MapTR/data/nuscenes

# 1. 备份原始索引文件
mv nuscenes_infos_temporal_train.pkl nuscenes_infos_temporal_train.pkl.original
mv nuscenes_infos_temporal_val.pkl nuscenes_infos_temporal_val.pkl.original

# 2. 创建软链接指向新生成的索引
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl .
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_val.pkl .

# 3. 验证软链接
ls -lh nuscenes_infos_temporal*.pkl
```

然后使用原始配置文件训练即可。

### 恢复原始数据

```bash
cd /path/to/MapTR/data/nuscenes

# 删除软链接
rm nuscenes_infos_temporal_train.pkl
rm nuscenes_infos_temporal_val.pkl

# 恢复原始文件
mv nuscenes_infos_temporal_train.pkl.original nuscenes_infos_temporal_train.pkl
mv nuscenes_infos_temporal_val.pkl.original nuscenes_infos_temporal_val.pkl
```

---

## 🔍 验证配置

在训练前验证配置是否正确：

```python
# test_config.py
import pickle

# 检查pkl文件
with open('/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl', 'rb') as f:
    data = pickle.load(f)

print(f"样本数: {len(data['infos'])}")

# 检查第一个样本的路径
first_sample = data['infos'][0]
cam_path = first_sample['cams']['CAM_FRONT']['data_path']
print(f"相机路径: {cam_path}")

# 构造完整路径（假设data_root='data/nuscenes/'）
import os
full_path = os.path.join('data/nuscenes', cam_path.lstrip('./'))
print(f"完整路径: {full_path}")
print(f"文件存在: {os.path.exists(full_path)}")
```

---

## ⚠️ 常见错误

### 错误1：将maptr_balanced作为data_root

```python
# ❌ 错误！
data_root = '/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/'
ann_file = data_root + 'nuscenes_infos_temporal_train.pkl'
```

**问题**：找不到 `samples/`, `sweeps/` 等目录  
**错误信息**：`FileNotFoundError: samples/CAM_FRONT/xxx.jpg`

### 错误2：路径不一致

```python
# ❌ 错误！
data_root = '/different/path/to/nuscenes'  # 与生成pkl时的路径不同
```

**问题**：路径不匹配  
**解决**：确保data_root指向包含实际数据的nuscenes目录

---

## 📈 预期效果

使用平衡子集训练（21,222 samples vs 34,149 samples）：

| 指标 | 全量数据 | 平衡子集 | 变化 |
|------|---------|---------|------|
| 样本数 | 34,149 | 21,222 | -38% |
| 训练时间/epoch | 100% | ~62% | **↓38%** |
| 收敛速度 | Baseline | 可能更快 | **↑** |
| 性能 | XX.X mAP | 保持/提升 | **≈/↑** |

---

## 🎯 完整示例

### MapTR配置文件示例

```python
# projects/configs/maptr/maptr_nano_r18_110e_balanced.py

_base_ = [
    '../datasets/custom_nus-3d.py',
    '../_base_/default_runtime.py'
]

plugin = True
plugin_dir = 'projects/mmdet3d_plugin/'

# ... 其他配置不变 ...

# 只修改这里！
data = dict(
    samples_per_gpu=4,
    workers_per_gpu=4,
    train=dict(
        type='NuScenesDataset',
        data_root='data/nuscenes/',  # ← 保持原样
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_train.pkl',  # ← 修改这里
        pipeline=train_pipeline,
        classes=class_names,
        modality=input_modality,
        test_mode=False,
        box_type_3d='LiDAR'
    ),
    val=dict(
        type='NuScenesDataset',
        data_root='data/nuscenes/',  # ← 保持原样
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced/nuscenes_infos_temporal_val.pkl',  # ← 修改这里
        pipeline=test_pipeline,
        classes=class_names,
        modality=input_modality,
        test_mode=True,
        box_type_3d='LiDAR'
    ),
)
```

---

## 🚀 开始训练

```bash
cd /path/to/MapTR

# 单GPU训练
python tools/train.py projects/configs/maptr/maptr_nano_r18_110e_balanced.py

# 多GPU训练（推荐）
./tools/dist_train.sh \
    projects/configs/maptr/maptr_nano_r18_110e_balanced.py \
    8 \
    --work-dir work_dirs/maptr_balanced
```

---

## 📝 总结

| 项目 | 说明 |
|------|------|
| **maptr_balanced/** | 只包含索引文件，不能直接作为data_root |
| **data_root** | 必须指向包含实际数据（samples/sweeps/）的目录 |
| **ann_file** | 指向maptr_balanced中的pkl文件 |
| **修改方式** | 方法1: 修改配置文件；方法2: 使用软链接 |

---

## 💡 提示

1. **推荐方法1**（修改配置文件）- 更清晰、易于管理
2. 训练前先用小batch测试配置是否正确
3. 记录实验结果，对比全量数据和平衡子集的性能
4. 可以尝试其他生成模式（如纯低冗余度）进行对比

有任何问题随时问我！🚀

