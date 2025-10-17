# 文档索引

快速找到你需要的文档和脚本。

## 📖 文档导航

### 🚀 新手入门

| 文档 | 内容 | 阅读时间 |
|------|------|---------|
| **[GETTING_STARTED.md](GETTING_STARTED.md)** | **最简单的入门指南** | 5分钟 |
| [QUICKSTART.md](QUICKSTART.md) | 快速开始指南 | 3分钟 |
| [SUMMARY.md](SUMMARY.md) | 项目总览和使用场景 | 10分钟 |

**推荐路径**：GETTING_STARTED.md → QUICKSTART.md → 实际操作

### 📚 详细文档

| 文档 | 内容 | 适合人群 |
|------|------|---------|
| [README.md](README.md) | 完整功能文档 | 所有用户 |
| [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) | MapTR集成详细指南 | MapTR用户 |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构和原理 | 开发者 |

### 🎯 按需求查找

#### 我想快速了解这个项目
→ [GETTING_STARTED.md](GETTING_STARTED.md) + [SUMMARY.md](SUMMARY.md)

#### 我要分析NuScenes数据冗余度
→ [README.md](README.md) 的"数据划分"部分

#### 我要在MapTR中使用
→ [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md)

#### 我想自定义开发
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

#### 我遇到了问题
→ [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) 的"故障排除"部分

## 🔧 脚本索引

### 核心功能脚本

| 脚本 | 功能 | 用途 |
|------|------|------|
| **[split_by_redundancy.py](split_by_redundancy.py)** | **冗余度分析** | 分析数据集，生成划分结果 |
| [visualize_redundancy.py](visualize_redundancy.py) | 可视化 | 生成图表和统计 |
| [redundancy_utils.py](redundancy_utils.py) | 工具类库 | 加载和使用划分结果 |
| [usage_example.py](usage_example.py) | 使用示例 | 学习如何使用 |

### MapTR集成脚本

| 脚本 | 功能 | 用途 |
|------|------|------|
| **[maptr_adapter.py](maptr_adapter.py)** | **MapTR适配器** | 生成MapTR数据格式 |
| [maptr_example.py](maptr_example.py) | MapTR示例 | MapTR使用示例 |
| [generate_maptr_data.sh](generate_maptr_data.sh) | 一键生成 | 快速生成MapTR数据 |

### 便捷脚本

| 脚本 | 功能 | 用途 |
|------|------|------|
| [run_example.sh](run_example.sh) | 一键运行 | 完整流程演示 |

## 📋 快速命令参考

### 基础使用

```bash
# 冗余度分析
python split_by_redundancy.py

# 可视化结果
python visualize_redundancy.py

# 查看示例
python usage_example.py
```

### MapTR集成

```bash
# 方式1：一键生成（推荐新手）
./generate_maptr_data.sh

# 方式2：命令行（推荐熟练用户）
python maptr_adapter.py --mode low_only

# 方式3：Python API（推荐开发者）
python maptr_example.py
```

### 完整流程

```bash
# 一键完成所有操作
./run_example.sh && ./generate_maptr_data.sh
```

## 🎓 学习路径

### 路径1：纯冗余度分析（30分钟）

1. 阅读 [GETTING_STARTED.md](GETTING_STARTED.md) (5分钟)
2. 运行 `./run_example.sh` (5分钟)
3. 查看生成的报告和图表 (10分钟)
4. 阅读 [README.md](README.md) (10分钟)

### 路径2：MapTR集成（1小时）

1. 完成路径1
2. 阅读 [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) (15分钟)
3. 运行 `./generate_maptr_data.sh` (5分钟)
4. 在MapTR中测试 (20分钟)
5. 对比实验 (根据需要)

### 路径3：深入开发（2小时+）

1. 完成路径1和路径2
2. 阅读 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) (20分钟)
3. 阅读源代码注释 (30分钟)
4. 自定义开发 (根据需要)

## 📊 按角色推荐

### 🎯 研究人员

**目标**：提高实验效率

**推荐阅读**：
1. [SUMMARY.md](SUMMARY.md) - 了解能做什么
2. [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) - 集成到现有流程
3. [README.md](README.md) - 详细参数

**推荐脚本**：
- `./generate_maptr_data.sh` - 快速生成数据
- `python maptr_adapter.py --mode custom` - 自定义实验

### 👨‍💻 开发者

**目标**：理解原理，自定义功能

**推荐阅读**：
1. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - 项目架构
2. 源代码注释 - 实现细节
3. [README.md](README.md) - API文档

**推荐脚本**：
- `redundancy_utils.py` - 工具类库
- `maptr_adapter.py` - 适配器示例

### 👩‍🎓 学生

**目标**：学习和理解

**推荐阅读**：
1. [GETTING_STARTED.md](GETTING_STARTED.md) - 从零开始
2. [SUMMARY.md](SUMMARY.md) - 理解概念
3. [README.md](README.md) - 深入学习

**推荐脚本**：
- `./run_example.sh` - 看看效果
- `usage_example.py` - 学习用法

### 🔧 工程师

**目标**：快速部署，优化流程

**推荐阅读**：
1. [QUICKSTART.md](QUICKSTART.md) - 快速部署
2. [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) - 生产环境
3. [SUMMARY.md](SUMMARY.md) 的"最佳实践"

**推荐脚本**：
- `./generate_maptr_data.sh` - 自动化
- `python maptr_adapter.py` - 集成脚本

## 🔍 问题解决

### 我不知道从哪里开始
→ [GETTING_STARTED.md](GETTING_STARTED.md)

### 我想了解原理
→ [README.md](README.md) 的"工作原理"部分

### 我要在MapTR中使用
→ [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md)

### 脚本报错了
→ [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) 的"故障排除"

### 我想调整参数
→ [README.md](README.md) 的"参数调优建议"

### 我想自定义功能
→ [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) + 源代码

### 性能不如预期
→ [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md) 的"故障排除"

## 📁 文件大小参考

| 文件 | 大小 | 类型 |
|------|------|------|
| split_by_redundancy.py | 15K | Python脚本 |
| maptr_adapter.py | 16K | Python脚本 |
| redundancy_utils.py | 13K | Python库 |
| visualize_redundancy.py | 12K | Python脚本 |
| usage_example.py | 8.4K | Python示例 |
| maptr_example.py | 8.8K | Python示例 |
| MAPTR_INTEGRATION.md | 8.9K | 文档 |
| README.md | 7.8K | 文档 |
| SUMMARY.md | 8.0K | 文档 |
| GETTING_STARTED.md | 6.3K | 文档 |
| PROJECT_STRUCTURE.md | 6.7K | 文档 |
| generate_maptr_data.sh | 4.2K | Shell脚本 |
| QUICKSTART.md | 2.6K | 文档 |
| run_example.sh | 2.1K | Shell脚本 |

## 🎯 快速操作

### 我就想快速用起来

```bash
# 1. 一行命令完成所有
./run_example.sh && ./generate_maptr_data.sh

# 2. 在MapTR中使用（修改配置文件路径即可）
```

**阅读时间**：0分钟  
**操作时间**：10分钟

### 我想理解后再使用

**第一步**：阅读 [GETTING_STARTED.md](GETTING_STARTED.md) (5分钟)  
**第二步**：运行 `./run_example.sh` 看效果 (5分钟)  
**第三步**：阅读 [README.md](README.md) 理解原理 (10分钟)  
**第四步**：运行 `./generate_maptr_data.sh` 生成MapTR数据 (2分钟)

**总时间**：22分钟

### 我要深入研究

**建议顺序**：
1. GETTING_STARTED.md → 了解基础
2. README.md → 完整功能
3. PROJECT_STRUCTURE.md → 项目架构
4. 阅读源代码 → 实现细节
5. MAPTR_INTEGRATION.md → 实际应用

**总时间**：2-3小时

## 📞 获取帮助

1. **查找文档**：使用本索引快速定位
2. **查看示例**：运行example脚本
3. **阅读注释**：所有代码都有详细JSDoc注释
4. **检查日志**：查看脚本输出信息

## ✨ 推荐起点

**如果你是...**

- **完全新手** → [GETTING_STARTED.md](GETTING_STARTED.md)
- **想快速使用** → [QUICKSTART.md](QUICKSTART.md)
- **MapTR用户** → [MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md)
- **想了解全貌** → [SUMMARY.md](SUMMARY.md)
- **需要完整文档** → [README.md](README.md)
- **要深入开发** → [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 🎉 开始你的旅程

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 选择你的路径
# 路径1：快速体验
./run_example.sh

# 路径2：MapTR集成
./generate_maptr_data.sh

# 路径3：深入学习
cat GETTING_STARTED.md
```

祝使用愉快！🚀

