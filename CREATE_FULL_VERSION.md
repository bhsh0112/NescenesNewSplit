# 创建完整的NuScenes版本

## 🎯 功能说明

本工具可以创建**完整的NuScenes版本**，包含所有元数据和数据结构，而不仅仅是索引文件。

### 与索引文件方式的区别

| 方式 | 内容 | 使用 | 空间占用 |
|------|------|------|---------|
| **索引文件** | 只有pkl文件 | 需要指定ann_file | 极小(~200MB) |
| **完整版本** | 完整的v1.0-xxx结构 | 直接作为data_root | 较小(使用链接) |

## 📦 生成内容

运行后会生成类似原始NuScenes的完整目录结构：

```
nuscenes_versions/
├── v1.0-high-redundancy/          # 高冗余度版本
│   ├── sample.json                # 元数据（仅包含高冗余度samples）
│   ├── scene.json                 # 元数据（相关scenes）
│   ├── sample_data.json           # 元数据（相关sample_data）
│   ├── ego_pose.json              # 元数据（相关ego_poses）
│   ├── calibrated_sensor.json
│   ├── sensor.json
│   ├── log.json
│   └── ...
│
├── v1.0-low-redundancy/           # 低冗余度版本
│   ├── sample.json                # 元数据（仅包含低冗余度samples）
│   └── ...
│
├── samples/ → 符号链接到原始数据
├── sweeps/ → 符号链接到原始数据
└── maps/ → 符号链接到原始数据
```

## 🚀 使用方法

### 方法1：使用脚本（推荐）

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 运行创建脚本
./create_versions.sh

# 按提示选择：
# 1) 高冗余度版本
# 2) 低冗余度版本
# 3) 同时创建两个版本
```

### 方法2：命令行

```bash
# 创建低冗余度版本
python create_nuscenes_version.py \
    --create-low \
    --use-symlink

# 创建高冗余度版本
python create_nuscenes_version.py \
    --create-high \
    --use-symlink

# 同时创建两个版本
python create_nuscenes_version.py \
    --create-both \
    --use-symlink
```

## 📋 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--original-dataroot` | 原始NuScenes路径 | `./data/nuscenes` |
| `--original-version` | 原始版本名称 | `v1.0-trainval` |
| `--redundancy-split` | 冗余度划分结果 | `./redundancy_split/redundancy_split.pkl` |
| `--output-dataroot` | 输出目录 | `./nuscenes_versions` |
| `--create-high` | 创建高冗余度版本 | - |
| `--create-low` | 创建低冗余度版本 | - |
| `--create-both` | 创建两个版本 | - |
| `--use-symlink` | 使用符号链接 | `True` |

## 💾 空间占用

### 使用符号链接（推荐）

```
高冗余度版本: ~50MB (仅元数据JSON文件)
低冗余度版本: ~100MB (仅元数据JSON文件)
数据文件: 0 (使用符号链接，不占额外空间)
```

### 使用硬链接

```
高冗余度版本: ~50MB + 数据文件索引
低冗余度版本: ~100MB + 数据文件索引
数据文件: 0 (硬链接，不占额外空间)
```

### 完整复制（不推荐）

```
会复制所有数据文件，占用大量空间（几百GB）
```

## 📊 数据统计

基于你的冗余度分析结果：

### 高冗余度版本
- **Samples**: 8,845
- **Scenes**: 220
- **特点**: 车辆静止或缓慢移动的场景

### 低冗余度版本
- **Samples**: 18,230
- **Scenes**: 454
- **特点**: 车辆快速移动，场景变化大

## 🎮 在MapTR中使用

### 配置文件设置

```python
# projects/configs/maptr/maptr_nano_r18_110e_low.py

_base_ = [
    '../datasets/custom_nus-3d.py',
    '../_base_/default_runtime.py'
]

# 直接设置data_root为新版本
data_root = './nuscenes_versions/v1.0-low-redundancy/'

data = dict(
    samples_per_gpu=4,
    workers_per_gpu=4,
    train=dict(
        type='NuScenesDataset',
        data_root=data_root,  # 使用新版本
        ann_file=data_root + 'nuscenes_infos_temporal_train.pkl',  # 还需要生成这个
        # ...
    ),
)
```

### 注意事项

⚠️ **还需要生成对应的pkl索引文件！**

创建完整版本后，还需要使用MapTR的数据准备工具生成pkl：

```bash
cd /path/to/MapTR

python tools/create_data.py nuscenes \
    --root-path ./nuscenes_versions/v1.0-low-redundancy \
    --out-dir ./nuscenes_versions/v1.0-low-redundancy \
    --extra-tag nuscenes \
    --version v1.0-low-redundancy \
    --canbus ./data
```

## 🔄 工作流程

### 完整流程

```bash
# 1. 分析冗余度
python split_by_redundancy.py

# 2. 创建完整版本
./create_versions.sh

# 3. 在MapTR中生成pkl索引
cd /path/to/MapTR
python tools/create_data.py nuscenes \
    --root-path /path/to/nuscenes_versions/v1.0-low-redundancy \
    --out-dir /path/to/nuscenes_versions/v1.0-low-redundancy \
    --extra-tag nuscenes \
    --version v1.0-low-redundancy

# 4. 训练MapTR
./tools/dist_train.sh \
    projects/configs/maptr/your_config.py \
    8
```

## 🆚 两种方法对比

### 方法A：完整版本（本工具）

**优点**：
- ✅ 目录结构清晰，完全独立
- ✅ 可以直接作为data_root使用
- ✅ 符合NuScenes标准格式
- ✅ 便于管理和迁移

**缺点**：
- ❌ 需要额外的创建步骤
- ❌ 占用一些空间（虽然很小）

**适用场景**：
- 需要长期使用特定子集
- 需要在多个项目中共享
- 需要标准的NuScenes格式

### 方法B：索引文件（之前的方法）

**优点**：
- ✅ 生成速度快
- ✅ 占用空间极小
- ✅ 简单直接

**缺点**：
- ❌ 需要修改配置文件指定ann_file
- ❌ 不是标准NuScenes结构
- ❌ data_root仍需要指向原始数据

**适用场景**：
- 快速实验
- 临时使用
- 不需要独立版本

## 💡 推荐使用场景

### 使用完整版本（方法A）当你：
1. 需要发布或分享特定子集
2. 需要在多个实验中重复使用
3. 希望有清晰的版本管理
4. 需要标准的NuScenes格式

### 使用索引文件（方法B）当你：
1. 快速验证想法
2. 一次性实验
3. 硬盘空间极其有限
4. 只需要修改训练集

## 📝 示例

### 示例1：创建低冗余度版本用于快速训练

```bash
# 1. 创建版本
python create_nuscenes_version.py --create-low

# 2. 生成MapTR索引
cd /path/to/MapTR
python tools/create_data.py nuscenes \
    --root-path /path/to/nuscenes_versions/v1.0-low-redundancy \
    --out-dir /path/to/nuscenes_versions/v1.0-low-redundancy \
    --extra-tag nuscenes \
    --version v1.0-low-redundancy

# 3. 使用
# 在MapTR配置中：
# data_root = './nuscenes_versions/v1.0-low-redundancy/'
```

### 示例2：对比高低冗余度性能

```bash
# 创建两个版本
python create_nuscenes_version.py --create-both

# 对每个版本生成MapTR索引
# ...

# 分别训练
./tools/dist_train.sh config_high.py 8 --work-dir work_dirs/high_redundancy
./tools/dist_train.sh config_low.py 8 --work-dir work_dirs/low_redundancy

# 对比结果
```

## 🔧 故障排除

### 问题1：创建时间很长
**原因**：正在复制大量文件  
**解决**：确保使用 `--use-symlink` 参数

### 问题2：找不到图像文件
**原因**：符号链接失效  
**解决**：检查原始nuscenes路径是否正确

### 问题3：MapTR找不到pkl文件
**原因**：忘记生成pkl索引  
**解决**：在新版本目录中运行 `tools/create_data.py`

## 📚 相关文档

- `HOW_TO_USE_WITH_MAPTR.md` - 使用索引文件的方法
- `MAPTR_INTEGRATION.md` - MapTR集成详细指南
- `README.md` - 主文档

## 🎉 总结

现在你有两种方式：

1. **完整版本**（本文档）：创建独立的v1.0-xxx版本，可直接作为data_root
2. **索引文件**（之前）：只生成pkl索引，需要指定ann_file

选择适合你需求的方式！推荐使用完整版本以获得更好的管理体验。

