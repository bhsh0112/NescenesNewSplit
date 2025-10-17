#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MapTR适配器使用示例
演示如何生成不同配置的MapTR数据
"""

import os
from maptr_adapter import MapTRAdapter


def example1_low_redundancy_only():
    """
    示例1：仅使用低冗余度数据
    这是最推荐的方式，可以显著提高训练速度
    """
    print("\n" + "=" * 80)
    print("示例1：生成仅包含低冗余度的MapTR数据")
    print("=" * 80)
    
    # 配置路径
    redundancy_split = './redundancy_split/redundancy_split.pkl'
    original_train = './data/nuscenes/nuscenes_infos_temporal_train.pkl'
    original_val = './data/nuscenes/nuscenes_infos_temporal_val.pkl'
    output_dir = './maptr_low_redundancy'
    
    # 检查文件
    if not os.path.exists(redundancy_split):
        print(f"错误: 找不到文件 {redundancy_split}")
        print("请先运行 split_by_redundancy.py")
        return
    
    if not os.path.exists(original_train) or not os.path.exists(original_val):
        print("错误: 找不到原始MapTR数据文件")
        print("请先准备MapTR数据")
        return
    
    # 创建适配器
    adapter = MapTRAdapter(redundancy_split)
    
    # 生成低冗余度数据
    result = adapter.create_low_redundancy_split(
        original_train_path=original_train,
        original_val_path=original_val,
        output_dir=output_dir,
        include_categories=['low_redundancy']
    )
    
    print(f"\n✓ 成功生成低冗余度MapTR数据")
    print(f"  训练集: {result['train_count']} samples")
    print(f"  验证集: {result['val_count']} samples")
    print(f"  输出目录: {output_dir}")


def example2_mixed_redundancy():
    """
    示例2：混合不同冗余度的数据
    包含70%低冗余度 + 30%中冗余度
    """
    print("\n" + "=" * 80)
    print("示例2：生成混合冗余度的MapTR数据")
    print("=" * 80)
    
    redundancy_split = './redundancy_split/redundancy_split.pkl'
    original_train = './data/nuscenes/nuscenes_infos_temporal_train.pkl'
    original_val = './data/nuscenes/nuscenes_infos_temporal_val.pkl'
    output_dir = './maptr_mixed'
    
    if not os.path.exists(redundancy_split):
        print(f"错误: 找不到文件 {redundancy_split}")
        return
    
    if not os.path.exists(original_train) or not os.path.exists(original_val):
        print("错误: 找不到原始MapTR数据文件")
        return
    
    adapter = MapTRAdapter(redundancy_split)
    
    # 生成混合数据：70%低冗余 + 30%中冗余
    result = adapter.create_custom_split(
        original_train_path=original_train,
        original_val_path=original_val,
        output_dir=output_dir,
        low_ratio=0.7,        # 70%的低冗余度样本
        medium_ratio=0.3,     # 30%的中冗余度样本
        high_ratio=0.0,       # 0%的高冗余度样本
        random_state=42
    )
    
    print(f"\n✓ 成功生成混合冗余度MapTR数据")
    print(f"  训练集: {result['train_count']} samples")
    print(f"  验证集: {result['val_count']} samples")
    print(f"  输出目录: {output_dir}")


def example3_balanced_split():
    """
    示例3：平衡的冗余度划分
    从高、中、低冗余度各取相同数量的样本
    """
    print("\n" + "=" * 80)
    print("示例3：生成平衡冗余度的MapTR数据")
    print("=" * 80)
    
    redundancy_split = './redundancy_split/redundancy_split.pkl'
    original_train = './data/nuscenes/nuscenes_infos_temporal_train.pkl'
    original_val = './data/nuscenes/nuscenes_infos_temporal_val.pkl'
    output_dir = './maptr_balanced'
    
    if not os.path.exists(redundancy_split):
        print(f"错误: 找不到文件 {redundancy_split}")
        return
    
    if not os.path.exists(original_train) or not os.path.exists(original_val):
        print("错误: 找不到原始MapTR数据文件")
        return
    
    adapter = MapTRAdapter(redundancy_split)
    
    # 生成平衡数据
    result = adapter.create_balanced_redundancy_split(
        original_train_path=original_train,
        original_val_path=original_val,
        output_dir=output_dir
    )
    
    print(f"\n✓ 成功生成平衡冗余度MapTR数据")
    print(f"  训练集: {result['train_count']} samples")
    print(f"  验证集: {result['val_count']} samples")
    print(f"  输出目录: {output_dir}")


def example4_low_and_medium():
    """
    示例4：包含低冗余度和中冗余度的所有样本
    """
    print("\n" + "=" * 80)
    print("示例4：生成低+中冗余度的MapTR数据")
    print("=" * 80)
    
    redundancy_split = './redundancy_split/redundancy_split.pkl'
    original_train = './data/nuscenes/nuscenes_infos_temporal_train.pkl'
    original_val = './data/nuscenes/nuscenes_infos_temporal_val.pkl'
    output_dir = './maptr_low_medium'
    
    if not os.path.exists(redundancy_split):
        print(f"错误: 找不到文件 {redundancy_split}")
        return
    
    if not os.path.exists(original_train) or not os.path.exists(original_val):
        print("错误: 找不到原始MapTR数据文件")
        return
    
    adapter = MapTRAdapter(redundancy_split)
    
    # 包含低冗余度和中冗余度的所有样本
    result = adapter.create_low_redundancy_split(
        original_train_path=original_train,
        original_val_path=original_val,
        output_dir=output_dir,
        include_categories=['low_redundancy', 'medium_redundancy']
    )
    
    print(f"\n✓ 成功生成低+中冗余度MapTR数据")
    print(f"  训练集: {result['train_count']} samples")
    print(f"  验证集: {result['val_count']} samples")
    print(f"  输出目录: {output_dir}")


def example5_custom_ratio():
    """
    示例5：自定义采样比例
    例如：50%低冗余 + 20%中冗余 + 10%高冗余
    """
    print("\n" + "=" * 80)
    print("示例5：自定义采样比例")
    print("=" * 80)
    
    redundancy_split = './redundancy_split/redundancy_split.pkl'
    original_train = './data/nuscenes/nuscenes_infos_temporal_train.pkl'
    original_val = './data/nuscenes/nuscenes_infos_temporal_val.pkl'
    output_dir = './maptr_custom_ratio'
    
    if not os.path.exists(redundancy_split):
        print(f"错误: 找不到文件 {redundancy_split}")
        return
    
    if not os.path.exists(original_train) or not os.path.exists(original_val):
        print("错误: 找不到原始MapTR数据文件")
        return
    
    adapter = MapTRAdapter(redundancy_split)
    
    # 自定义比例
    result = adapter.create_custom_split(
        original_train_path=original_train,
        original_val_path=original_val,
        output_dir=output_dir,
        low_ratio=0.5,       # 50%的低冗余度样本
        medium_ratio=0.2,    # 20%的中冗余度样本
        high_ratio=0.1,      # 10%的高冗余度样本
        random_state=42
    )
    
    print(f"\n✓ 成功生成自定义比例MapTR数据")
    print(f"  训练集: {result['train_count']} samples")
    print(f"  验证集: {result['val_count']} samples")
    print(f"  输出目录: {output_dir}")


def main():
    """
    运行所有示例
    """
    print("=" * 80)
    print("MapTR适配器使用示例")
    print("=" * 80)
    print("\n本脚本演示如何生成不同配置的MapTR数据")
    print("请确保已经运行了 split_by_redundancy.py 生成冗余度划分")
    print("\n可用示例：")
    print("  1. 仅低冗余度数据（推荐）")
    print("  2. 混合冗余度数据（70%低 + 30%中）")
    print("  3. 平衡冗余度数据")
    print("  4. 低+中冗余度数据")
    print("  5. 自定义采样比例")
    print("  0. 运行所有示例")
    print()
    
    try:
        choice = input("请选择示例 [0-5]: ").strip()
        
        if choice == '1':
            example1_low_redundancy_only()
        elif choice == '2':
            example2_mixed_redundancy()
        elif choice == '3':
            example3_balanced_split()
        elif choice == '4':
            example4_low_and_medium()
        elif choice == '5':
            example5_custom_ratio()
        elif choice == '0':
            example1_low_redundancy_only()
            example2_mixed_redundancy()
            example3_balanced_split()
            example4_low_and_medium()
            example5_custom_ratio()
        else:
            print("无效选择")
            return
        
        print("\n" + "=" * 80)
        print("示例运行完成！")
        print("=" * 80)
        print("\n提示：")
        print("1. 查看生成的报告文件了解详细统计信息")
        print("2. 在MapTR配置中修改数据路径即可使用生成的数据")
        print("3. 建议先在小规模数据上测试，确认效果后再全量训练")
        
    except KeyboardInterrupt:
        print("\n\n已取消")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == '__main__':
    main()

