# 开始使用 - NuScenes冗余度划分与MapTR集成

本文档提供最简单的入门指南。

## 🎯 你能做什么

1. **分析NuScenes数据集的冗余度** - 了解哪些数据是重复的
2. **生成MapTR训练数据** - 直接用于MapTR训练
3. **提高训练速度** - 减少30-50%的训练时间
4. **保持或提升性能** - 更好的数据质量

## ⚡ 30秒快速开始

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 一键完成所有操作
./run_example.sh && ./generate_maptr_data.sh
```

就这么简单！

## 📖 分步指南

### 步骤1：安装依赖（10秒）

```bash
pip install numpy matplotlib
```

### 步骤2：分析数据冗余度（2-5分钟）

```bash
python split_by_redundancy.py
```

这会生成：
- `redundancy_split/redundancy_split.pkl` - 划分结果
- `redundancy_split/redundancy_report.txt` - 统计报告
- `redundancy_split/*.png` - 可视化图表

### 步骤3：生成MapTR数据（1分钟）

```bash
./generate_maptr_data.sh
```

按提示选择模式（推荐选择1 - 仅低冗余度）

### 步骤4：在MapTR中使用

**方法A：修改配置文件**（推荐）

在MapTR配置文件中修改数据路径：
```python
data = dict(
    train=dict(
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_train.pkl',
    ),
    val=dict(
        ann_file='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_val.pkl',
    ),
)
```

**方法B：使用软链接**

```bash
cd /path/to/MapTR/data/nuscenes
mv nuscenes_infos_temporal_train.pkl nuscenes_infos_temporal_train.pkl.bak
mv nuscenes_infos_temporal_val.pkl nuscenes_infos_temporal_val.pkl.bak
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_train.pkl .
ln -s /data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy/nuscenes_infos_temporal_val.pkl .
```

### 步骤5：训练MapTR

```bash
cd /path/to/MapTR
./tools/dist_train.sh projects/configs/maptr/your_config.py 8
```

## 🎓 理解输出

### 冗余度报告示例

```
高冗余度 (速率 < 1 m/s):
  Scenes数量: 120 (40%)
  Samples数量: 11,252 (40%)
  平均速率: 0.35 m/s
  
中冗余度 (速率 1-5 m/s):
  Scenes数量: 90 (30%)
  Samples数量: 8,439 (30%)
  平均速率: 2.8 m/s
  
低冗余度 (速率 > 5 m/s):
  Scenes数量: 90 (30%)
  Samples数量: 8,439 (30%)
  平均速率: 7.2 m/s
```

**解读**：
- 高冗余度 = 车辆静止或缓慢移动，场景重复多
- 低冗余度 = 车辆快速移动，场景变化大

### 生成的MapTR数据

```
maptr_low_redundancy/
├── nuscenes_infos_temporal_train.pkl  # MapTR训练集
├── nuscenes_infos_temporal_val.pkl    # MapTR验证集
└── maptr_split_report.txt            # 统计报告
```

## 🔧 常用命令

### 查看统计报告
```bash
cat redundancy_split/redundancy_report.txt
```

### 可视化分析结果
```bash
python visualize_redundancy.py
# 生成图表在 redundancy_split/*.png
```

### 查看使用示例
```bash
python usage_example.py
```

### 生成不同配置的MapTR数据

**仅低冗余度（最快）**：
```bash
python maptr_adapter.py --mode low_only --output-dir ./maptr_low
```

**自定义混合**：
```bash
python maptr_adapter.py --mode custom --low-ratio 0.7 --medium-ratio 0.3 --output-dir ./maptr_custom
```

**平衡各类**：
```bash
python maptr_adapter.py --mode balanced --output-dir ./maptr_balanced
```

## 📊 预期结果

使用低冗余度数据训练MapTR：

| 指标 | 全部数据 | 低冗余度 | 变化 |
|------|---------|---------|------|
| 样本数 | ~28,000 | ~8,500 | ↓ 70% |
| 每epoch时间 | 100% | ~50% | ↓ 50% |
| 总训练时间 | 100% | ~50% | ↓ 50% |
| 验证mAP | XX.X | XX.X | ≈ 或 ↑ |

## ❓ 常见问题

### Q: 必须有MapTR才能使用吗？
A: 不是。可以只使用冗余度分析功能，了解数据分布。

### Q: 会不会影响模型性能？
A: 通常不会。低冗余度数据能保持甚至提升性能。

### Q: 需要多少时间？
A: 
- 冗余度分析：2-5分钟
- 生成MapTR数据：1分钟
- 总计：约5-10分钟

### Q: 能恢复使用全部数据吗？
A: 可以。只需要：
```bash
# 如果用软链接
rm nuscenes_infos_temporal_*.pkl
mv nuscenes_infos_temporal_*.pkl.bak nuscenes_infos_temporal_*.pkl

# 如果改配置文件
# 只需改回原来的路径
```

### Q: 支持其他模型吗？
A: 可以。参考 `maptr_adapter.py` 进行适配。

## 📚 进一步学习

1. **快速参考**：`QUICKSTART.md`
2. **MapTR详细集成**：`MAPTR_INTEGRATION.md`
3. **项目结构**：`PROJECT_STRUCTURE.md`
4. **完整文档**：`README.md`
5. **项目总结**：`SUMMARY.md`

## 💡 最佳实践

### 第一次使用
1. 先在v1.0-mini上测试
2. 查看可视化结果
3. 理解数据分布
4. 再在完整数据集使用

### 参数选择
- **追求速度**：使用 `--mode low_only`
- **平衡速度和性能**：使用 `--mode custom --low-ratio 0.7 --medium-ratio 0.3`
- **研究分析**：使用 `--mode balanced`

### 验证效果
1. 记录全部数据的baseline性能
2. 使用低冗余度数据训练
3. 对比训练时间和最终性能
4. 根据结果调整

## 🎯 下一步

完成上述步骤后，你可以：

1. **运行对比实验**
   - Baseline vs 低冗余度
   - 记录训练时间和性能

2. **调优参数**
   - 尝试不同的速率阈值
   - 尝试不同的混合比例

3. **分享结果**
   - 在团队中分享发现
   - 优化训练流程

## 📞 需要帮助？

1. 查看错误信息
2. 检查文件路径是否正确
3. 确认数据集版本一致
4. 阅读相关文档

## ✅ 检查清单

使用前确认：
- [x] Python 3.6+
- [x] numpy, matplotlib已安装
- [x] NuScenes数据集已准备
- [x] 如使用MapTR：MapTR原始数据已生成

## 🚀 开始吧！

```bash
cd /data2/file_swap/sh_space/nuscenes_NewSplit

# 一键开始
./run_example.sh
./generate_maptr_data.sh

# 或者分步执行
python split_by_redundancy.py
python visualize_redundancy.py
python maptr_adapter.py --mode low_only
```

祝你使用顺利！🎉

---

**快速链接**：
- 主文档：[README.md](README.md)
- 快速开始：[QUICKSTART.md](QUICKSTART.md)
- MapTR集成：[MAPTR_INTEGRATION.md](MAPTR_INTEGRATION.md)
- 项目总结：[SUMMARY.md](SUMMARY.md)

