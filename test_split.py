#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试冗余度分析（只分析前10个scenes）
"""

from split_by_redundancy import NuScenesRedundancySplitter

print("=" * 80)
print("测试冗余度分析（前10个scenes）")
print("=" * 80)

# 初始化
splitter = NuScenesRedundancySplitter(
    dataroot='./data/nuscenes',
    version='v1.0-trainval'
)

print(f"\n总共有 {len(splitter.scene)} 个scenes")
print("测试前10个scenes...\n")

# 只分析前10个scenes
test_results = []
for i, scene in enumerate(splitter.scene[:10]):
    result = splitter.analyze_scene(
        scene['token'],
        low_threshold=1.0,
        high_threshold=5.0
    )
    test_results.append(result)
    print(f"{i+1}. {result['scene_name']}: "
          f"速率={result['avg_velocity']:.2f} m/s, "
          f"冗余度={result['avg_redundancy']:.3f}, "
          f"samples={result['num_samples']}")

print("\n✓ 测试成功！现在可以运行完整分析了。")
print("\n运行完整分析:")
print("  python split_by_redundancy.py")

