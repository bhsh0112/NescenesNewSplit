#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用示例：演示如何使用冗余度划分工具
"""

import os
from redundancy_utils import RedundancySplitLoader


def example_basic_usage():
    """示例1：基本使用"""
    print("=" * 80)
    print("示例1：基本使用")
    print("=" * 80)
    
    # 加载划分结果
    split_path = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    
    if not os.path.exists(split_path):
        print(f"错误: 找不到划分结果文件: {split_path}")
        print("请先运行 split_by_redundancy.py 生成划分结果")
        return
    
    loader = RedundancySplitLoader(split_path)
    
    # 打印摘要
    loader.print_summary()
    
    # 获取各类别的样本数
    print("\n详细信息:")
    for category in ['high_redundancy', 'medium_redundancy', 'low_redundancy']:
        samples = loader.get_samples_by_category(category)
        scenes = loader.get_scenes_by_category(category)
        print(f"  {category}: {len(scenes)} scenes, {len(samples)} samples")


def example_sample_filtering():
    """示例2：样本筛选"""
    print("\n" + "=" * 80)
    print("示例2：样本筛选 - 只使用低冗余度数据")
    print("=" * 80)
    
    split_path = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    
    if not os.path.exists(split_path):
        print(f"错误: 找不到划分结果文件")
        return
    
    loader = RedundancySplitLoader(split_path)
    
    # 获取低冗余度样本
    low_redundancy_samples = loader.get_samples_by_category('low_redundancy')
    print(f"\n低冗余度样本总数: {len(low_redundancy_samples)}")
    
    # 获取低冗余度子集（包含部分中冗余度数据）
    subset = loader.get_low_redundancy_subset(ratio=0.7, random_state=42)
    print(f"低冗余度子集（70%低+30%中）: {len(subset)} samples")
    
    # 可以将这些token保存起来用于训练
    output_file = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/low_redundancy_subset.txt'
    with open(output_file, 'w') as f:
        for token in subset:
            f.write(f"{token}\n")
    print(f"\n已保存到: {output_file}")


def example_balanced_split():
    """示例3：创建平衡的训练/验证/测试划分"""
    print("\n" + "=" * 80)
    print("示例3：创建平衡的训练/验证/测试划分")
    print("=" * 80)
    
    split_path = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    
    if not os.path.exists(split_path):
        print(f"错误: 找不到划分结果文件")
        return
    
    loader = RedundancySplitLoader(split_path)
    
    # 按场景划分（推荐）
    split = loader.get_balanced_split(
        train_ratio=0.7,
        val_ratio=0.15,
        test_ratio=0.15,
        random_state=42,
        by_scene=True  # 确保同一场景的样本在同一个集合中
    )
    
    print(f"\n平衡划分结果（按场景）:")
    print(f"  训练集: {len(split['train'])} samples")
    print(f"  验证集: {len(split['val'])} samples")
    print(f"  测试集: {len(split['test'])} samples")
    
    # 保存划分结果
    output_dir = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split'
    for split_name, tokens in split.items():
        output_file = os.path.join(output_dir, f'balanced_{split_name}.txt')
        with open(output_file, 'w') as f:
            for token in tokens:
                f.write(f"{token}\n")
        print(f"  已保存 {split_name}: {output_file}")


def example_query_sample():
    """示例4：查询样本信息"""
    print("\n" + "=" * 80)
    print("示例4：查询样本信息")
    print("=" * 80)
    
    split_path = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    
    if not os.path.exists(split_path):
        print(f"错误: 找不到划分结果文件")
        return
    
    loader = RedundancySplitLoader(split_path)
    
    # 获取一些样本token用于演示
    low_samples = loader.get_samples_by_category('low_redundancy')
    high_samples = loader.get_samples_by_category('high_redundancy')
    
    if low_samples and high_samples:
        # 查询样本所属类别
        sample1 = low_samples[0]
        sample2 = high_samples[0]
        
        print(f"\n样本查询:")
        print(f"  样本1 ({sample1[:16]}...): {loader.get_category_by_sample(sample1)}")
        print(f"  样本2 ({sample2[:16]}...): {loader.get_category_by_sample(sample2)}")
        
        # 可以在数据加载时使用这个信息来过滤样本
        print(f"\n使用场景：在数据加载时过滤高冗余度样本")


def example_scene_analysis():
    """示例5：场景级别分析"""
    print("\n" + "=" * 80)
    print("示例5：场景级别分析")
    print("=" * 80)
    
    split_path = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    
    if not os.path.exists(split_path):
        print(f"错误: 找不到划分结果文件")
        return
    
    loader = RedundancySplitLoader(split_path)
    
    # 获取每个类别速率最低和最高的场景
    print("\n各类别典型场景:")
    
    categories = {
        'high_redundancy': '高冗余度',
        'medium_redundancy': '中冗余度',
        'low_redundancy': '低冗余度'
    }
    
    for category, name in categories.items():
        scenes = loader.get_scenes_by_category(category)
        if scenes:
            # 按速率排序
            sorted_scenes = sorted(scenes, key=lambda x: x['avg_velocity'])
            
            print(f"\n{name}:")
            print(f"  最慢场景: {sorted_scenes[0]['scene_name']}, "
                  f"速率={sorted_scenes[0]['avg_velocity']:.2f} m/s, "
                  f"冗余度={sorted_scenes[0]['avg_redundancy']:.3f}")
            
            if len(sorted_scenes) > 1:
                print(f"  最快场景: {sorted_scenes[-1]['scene_name']}, "
                      f"速率={sorted_scenes[-1]['avg_velocity']:.2f} m/s, "
                      f"冗余度={sorted_scenes[-1]['avg_redundancy']:.3f}")


def example_custom_training_split():
    """示例6：自定义训练策略"""
    print("\n" + "=" * 80)
    print("示例6：自定义训练策略 - 低冗余度为主，少量高冗余度")
    print("=" * 80)
    
    split_path = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    
    if not os.path.exists(split_path):
        print(f"错误: 找不到划分结果文件")
        return
    
    loader = RedundancySplitLoader(split_path)
    
    # 获取所有低冗余度样本
    low_samples = loader.get_samples_by_category('low_redundancy')
    
    # 获取部分中冗余度样本
    medium_samples = loader.sample_from_category('medium_redundancy', 
                                                 n=len(low_samples) // 2,
                                                 random_state=42)
    
    # 获取少量高冗余度样本（用于数据增强）
    high_samples = loader.sample_from_category('high_redundancy',
                                              n=len(low_samples) // 4,
                                              random_state=42)
    
    # 组合训练集
    training_samples = low_samples + medium_samples + high_samples
    
    print(f"\n自定义训练集组成:")
    print(f"  低冗余度: {len(low_samples)} samples")
    print(f"  中冗余度: {len(medium_samples)} samples")
    print(f"  高冗余度: {len(high_samples)} samples")
    print(f"  总计: {len(training_samples)} samples")
    
    # 保存训练集
    output_file = '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/custom_training_samples.txt'
    with open(output_file, 'w') as f:
        for token in training_samples:
            f.write(f"{token}\n")
    print(f"\n已保存到: {output_file}")


def main():
    """运行所有示例"""
    # 示例1：基本使用
    example_basic_usage()
    
    # 示例2：样本筛选
    example_sample_filtering()
    
    # 示例3：平衡划分
    example_balanced_split()
    
    # 示例4：查询样本
    example_query_sample()
    
    # 示例5：场景分析
    example_scene_analysis()
    
    # 示例6：自定义训练策略
    example_custom_training_split()
    
    print("\n" + "=" * 80)
    print("所有示例运行完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()

