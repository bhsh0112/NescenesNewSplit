# 两种MapTR集成方式对比

## 🎯 核心区别

你现在有**两种方式**将冗余度划分结果用于MapTR：

| 对比项 | 方式1：完整版本⭐ | 方式2：索引文件 |
|--------|------------------|----------------|
| **生成内容** | 完整的v1.0-xxx目录结构 | 仅pkl索引文件 |
| **包含文件** | sample.json等所有元数据 | nuscenes_infos_temporal_*.pkl |
| **data_root** | 指向新版本目录 | 仍指向原始nuscenes |
| **ann_file** | 自动匹配 | 需要特别指定 |
| **空间占用** | ~100MB（符号链接） | ~200MB |
| **创建时间** | 5-10分钟 | 1-2分钟 |
| **使用方式** | 直接作为独立数据集 | 需配合原始数据 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 📋 方式1：创建完整版本（推荐）

### 生成方式

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 方法A：使用脚本（最简单）
./create_versions.sh

# 方法B：命令行
python create_nuscenes_version.py --create-both
```

### 生成内容

```
nuscenes_versions/
├── v1.0-high-redundancy/          # 完整的高冗余度版本
│   ├── sample.json                # 8,845 samples
│   ├── scene.json
│   ├── sample_data.json
│   ├── ego_pose.json
│   └── ...
├── v1.0-low-redundancy/           # 完整的低冗余度版本
│   ├── sample.json                # 18,230 samples
│   └── ...
├── samples/ → 符号链接
├── sweeps/ → 符号链接
└── maps/ → 符号链接
```

### MapTR配置

```python
# 直接设置data_root
data_root = './nuscenes_versions/v1.0-low-redundancy/'

data = dict(
    train=dict(
        data_root=data_root,  # 使用新版本
        ann_file=data_root + 'nuscenes_infos_temporal_train.pkl',
    ),
)
```

### 优点
- ✅ 完整的NuScenes标准结构
- ✅ 可以直接作为独立数据集
- ✅ 便于版本管理和迁移
- ✅ 符合NuScenes官方格式
- ✅ 使用符号链接，几乎不占额外空间

### 缺点
- ❌ 需要额外的创建步骤
- ❌ 还需要运行MapTR的create_data.py生成pkl

---

## 📋 方式2：仅生成索引文件

### 生成方式

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 方法A：使用脚本
./generate_maptr_data.sh

# 方法B：命令行
python maptr_adapter.py --mode low_only
```

### 生成内容

```
maptr_low_redundancy/
├── nuscenes_infos_temporal_train.pkl    # 索引文件
├── nuscenes_infos_temporal_val.pkl      # 索引文件
└── maptr_split_report.txt               # 报告
```

### MapTR配置

```python
# data_root仍指向原始数据
data_root = 'data/nuscenes/'

data = dict(
    train=dict(
        data_root=data_root,  # 原始数据
        ann_file='/path/to/maptr_low_redundancy/nuscenes_infos_temporal_train.pkl',  # 新索引
    ),
)
```

### 优点
- ✅ 生成速度快
- ✅ 占用空间小
- ✅ 不需要额外步骤

### 缺点
- ❌ 需要修改配置指定ann_file
- ❌ 不是标准NuScenes结构
- ❌ data_root必须指向原始数据

---

## 🤔 如何选择？

### 选择方式1（完整版本）如果你：
1. ✅ 需要长期使用这个子集
2. ✅ 希望有清晰的版本管理
3. ✅ 需要在多个项目中使用
4. ✅ 想要标准的NuScenes格式
5. ✅ 计划分享给他人使用

### 选择方式2（索引文件）如果你：
1. ✅ 只是快速实验验证
2. ✅ 一次性使用
3. ✅ 不想改动原始数据结构
4. ✅ 硬盘空间非常有限

---

## 📊 实际对比

### 你的数据

根据冗余度分析结果：

| 版本 | Samples | Scenes | 占比 |
|------|---------|--------|------|
| 原始数据 | 34,149 | 850 | 100% |
| 高冗余度 | 8,845 | 220 | 26% |
| 低冗余度 | 18,230 | 454 | 53% |

### 训练时间预估

| 数据集 | 每epoch时间 | 总训练时间 |
|--------|------------|-----------|
| 全量数据 | 100% | 100% |
| 低冗余度 | ~53% | **↓47%** |
| 高冗余度 | ~26% | **↓74%** |

---

## 🚀 推荐工作流

### 方案A：完整版本（推荐）⭐

```bash
# 1. 分析冗余度
python split_by_redundancy.py

# 2. 创建完整版本
./create_versions.sh
# 选择：3) 同时创建两个版本

# 3. 生成MapTR索引（在MapTR目录中）
cd /path/to/MapTR
python tools/create_data.py nuscenes \
    --root-path /path/to/nuscenes_versions/v1.0-low-redundancy \
    --out-dir /path/to/nuscenes_versions/v1.0-low-redundancy \
    --extra-tag nuscenes \
    --version v1.0-low-redundancy

# 4. 修改配置
# data_root = './nuscenes_versions/v1.0-low-redundancy/'

# 5. 训练
./tools/dist_train.sh config.py 8
```

### 方案B：索引文件（快速）

```bash
# 1. 分析冗余度
python split_by_redundancy.py

# 2. 生成MapTR索引
./generate_maptr_data.sh
# 选择：1) 仅低冗余度数据

# 3. 修改配置
# data_root = 'data/nuscenes/'
# ann_file = '/path/to/maptr_low_redundancy/nuscenes_infos_temporal_train.pkl'

# 4. 训练
./tools/dist_train.sh config.py 8
```

---

## 💡 最佳实践

### 建议：使用方式1（完整版本）

**原因**：
1. 更清晰的版本管理
2. 符合NuScenes标准格式
3. 便于在多个实验中复用
4. 易于分享和迁移
5. 几乎不占额外空间（符号链接）

### 何时使用方式2

仅当你需要：
- 快速验证一个想法
- 临时测试
- 不需要独立版本管理

---

## 📝 示例场景

### 场景1：对比实验

使用方式1创建多个版本进行对比：

```bash
# 创建三个版本
python create_nuscenes_version.py \
    --output-dataroot ./nuscenes_versions \
    --create-both

# 分别训练对比
# 版本1：高冗余度
# 版本2：低冗余度
# 版本3：原始全量（baseline）
```

### 场景2：快速验证

使用方式2快速测试：

```bash
# 只生成索引
python maptr_adapter.py --mode low_only

# 修改配置
# 训练测试
```

---

## 🎉 总结

**推荐使用方式1（完整版本）** 🌟

它提供了更好的：
- 版本管理
- 可维护性
- 可复现性
- 标准化

现在你可以：

```bash
# 一键创建完整版本
cd /data2/file_swap/sh_space/nuscenes_NewSplit
./create_versions.sh
```

详细文档：
- 📄 [CREATE_FULL_VERSION.md](CREATE_FULL_VERSION.md) - 完整版本详细指南
- 📄 [HOW_TO_USE_WITH_MAPTR.md](HOW_TO_USE_WITH_MAPTR.md) - 索引文件使用说明

