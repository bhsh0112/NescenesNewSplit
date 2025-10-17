# 使用指南

## 快速开始

### 完整流程（推荐）

```bash
# 1. 分析冗余度和可视化（一键）
bash script/analyze_redundancy.sh

# 2. 创建完整版本（一键）
bash script/create_versions.sh
```

就这么简单！

## 两种MapTR集成方式

### 方式1：完整版本（推荐）⭐

生成完整的v1.0-xxx NuScenes版本结构

```bash
# 已由 create_versions.sh 创建
# 使用方法：直接作为 data_root
```

### 方式2：pkl索引文件

仅生成pkl索引，data_root仍指向原始数据

```bash
# 一键生成
bash script/generate_maptr_pkl.sh

# 或手动
python tools/generate_maptr_pkl.py --mode low_only
```

## 便捷脚本

| 脚本 | 功能 |
|------|------|
| `analyze_redundancy.sh` | 一键分析和可视化 |
| `create_versions.sh` | 一键创建完整版本 |
| `generate_maptr_pkl.sh` | 一键生成pkl索引 |

## 核心工具

| 工具 | 功能 |
|------|------|
| `split_by_redundancy.py` | 分析冗余度 |
| `create_nuscenes_version.py` | 创建完整版本 |
| `generate_maptr_pkl.py` | 生成pkl索引 |
| `visualize_redundancy.py` | 可视化 |

## 输出数据

- **高冗余度**: 8,845 samples (26%)
- **低冗余度**: 18,230 samples (53%)

详见 README.md
