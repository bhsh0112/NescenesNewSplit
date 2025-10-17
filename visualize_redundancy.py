#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化NuScenes数据集的冗余度分析结果
"""

import pickle
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import argparse

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
rcParams['axes.unicode_minus'] = False


def load_split_result(result_path: str):
    """
    加载划分结果
    
    Args:
        result_path: 结果文件路径（pkl或json）
        
    Returns:
        划分结果字典
    """
    if result_path.endswith('.pkl'):
        with open(result_path, 'rb') as f:
            return pickle.load(f)
    elif result_path.endswith('.json'):
        with open(result_path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError("不支持的文件格式，请使用.pkl或.json文件")


def plot_redundancy_distribution(split_result: dict, output_dir: str):
    """
    绘制冗余度分布图
    
    Args:
        split_result: 划分结果
        output_dir: 输出目录
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('NuScenes数据集冗余度分析', fontsize=16, fontweight='bold')
    
    # 1. 各类别的scene数量分布
    ax1 = axes[0, 0]
    categories = ['高冗余度', '中冗余度', '低冗余度']
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    scene_counts = [len(split_result[k]) for k in keys]
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    bars = ax1.bar(categories, scene_counts, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Scene数量', fontsize=12)
    ax1.set_title('各类别Scene数量分布', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # 在柱子上添加数值
    for bar, count in zip(bars, scene_counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 2. 各类别的sample数量分布
    ax2 = axes[0, 1]
    sample_counts = [sum(s['num_samples'] for s in split_result[k]) for k in keys]
    
    bars = ax2.bar(categories, sample_counts, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Sample数量', fontsize=12)
    ax2.set_title('各类别Sample数量分布', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    for bar, count in zip(bars, sample_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 3. 平均速率分布
    ax3 = axes[1, 0]
    velocities_by_category = []
    for key in keys:
        velocities = [s['avg_velocity'] for s in split_result[key]]
        velocities_by_category.append(velocities)
    
    bp = ax3.boxplot(velocities_by_category, labels=categories, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_ylabel('平均速率 (m/s)', fontsize=12)
    ax3.set_title('各类别平均速率分布', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. 冗余度分布
    ax4 = axes[1, 1]
    redundancies_by_category = []
    for key in keys:
        redundancies = [s['avg_redundancy'] for s in split_result[key]]
        redundancies_by_category.append(redundancies)
    
    bp = ax4.boxplot(redundancies_by_category, labels=categories, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax4.set_ylabel('冗余度分数', fontsize=12)
    ax4.set_title('各类别冗余度分布', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'redundancy_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"已保存分布图: {output_path}")
    plt.close()


def plot_velocity_histogram(split_result: dict, output_dir: str):
    """
    绘制速率直方图
    
    Args:
        split_result: 划分结果
        output_dir: 输出目录
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['高冗余度', '中冗余度', '低冗余度']
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    all_velocities = []
    for key, label, color in zip(keys, labels, colors):
        velocities = [s['avg_velocity'] for s in split_result[key]]
        all_velocities.extend(velocities)
        ax.hist(velocities, bins=30, alpha=0.6, label=label, color=color, edgecolor='black')
    
    ax.set_xlabel('平均速率 (m/s)', fontsize=12)
    ax.set_ylabel('Scene数量', fontsize=12)
    ax.set_title('各类别速率分布直方图', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'velocity_histogram.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"已保存速率直方图: {output_path}")
    plt.close()


def plot_redundancy_scatter(split_result: dict, output_dir: str):
    """
    绘制速率-冗余度散点图
    
    Args:
        split_result: 划分结果
        output_dir: 输出目录
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['高冗余度', '中冗余度', '低冗余度']
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    for key, label, color in zip(keys, labels, colors):
        velocities = [s['avg_velocity'] for s in split_result[key]]
        redundancies = [s['avg_redundancy'] for s in split_result[key]]
        sizes = [s['num_samples'] for s in split_result[key]]
        
        # 归一化size用于显示
        sizes_normalized = [s * 2 for s in sizes]  # 调整大小以便可视化
        
        ax.scatter(velocities, redundancies, s=sizes_normalized, alpha=0.6,
                  label=label, color=color, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('平均速率 (m/s)', fontsize=12)
    ax.set_ylabel('冗余度分数', fontsize=12)
    ax.set_title('速率-冗余度关系图\n(气泡大小表示sample数量)', 
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'redundancy_scatter.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"已保存散点图: {output_path}")
    plt.close()


def plot_pie_charts(split_result: dict, output_dir: str):
    """
    绘制饼图
    
    Args:
        split_result: 划分结果
        output_dir: 输出目录
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['高冗余度', '中冗余度', '低冗余度']
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    # Scene数量饼图
    scene_counts = [len(split_result[k]) for k in keys]
    axes[0].pie(scene_counts, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11})
    axes[0].set_title('Scene数量占比', fontsize=13, fontweight='bold')
    
    # Sample数量饼图
    sample_counts = [sum(s['num_samples'] for s in split_result[k]) for k in keys]
    axes[1].pie(sample_counts, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11})
    axes[1].set_title('Sample数量占比', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'redundancy_pie_charts.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"已保存饼图: {output_path}")
    plt.close()


def print_statistics(split_result: dict):
    """
    打印统计信息
    
    Args:
        split_result: 划分结果
    """
    print("\n" + "=" * 80)
    print("数据集划分统计")
    print("=" * 80)
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['高冗余度', '中冗余度', '低冗余度']
    
    total_scenes = sum(len(split_result[k]) for k in keys)
    total_samples = sum(sum(s['num_samples'] for s in split_result[k]) for k in keys)
    
    print(f"\n总计: {total_scenes} scenes, {total_samples} samples\n")
    
    for key, label in zip(keys, labels):
        scenes = split_result[key]
        num_scenes = len(scenes)
        num_samples = sum(s['num_samples'] for s in scenes)
        
        velocities = [s['avg_velocity'] for s in scenes]
        redundancies = [s['avg_redundancy'] for s in scenes]
        
        print(f"{label}:")
        print(f"  Scenes: {num_scenes} ({num_scenes/total_scenes*100:.1f}%)")
        print(f"  Samples: {num_samples} ({num_samples/total_samples*100:.1f}%)")
        
        if velocities:
            print(f"  速率统计:")
            print(f"    平均: {np.mean(velocities):.2f} m/s")
            print(f"    中位数: {np.median(velocities):.2f} m/s")
            print(f"    标准差: {np.std(velocities):.2f} m/s")
            print(f"    范围: [{np.min(velocities):.2f}, {np.max(velocities):.2f}] m/s")
        
        if redundancies:
            print(f"  冗余度统计:")
            print(f"    平均: {np.mean(redundancies):.3f}")
            print(f"    中位数: {np.median(redundancies):.3f}")
            print(f"    标准差: {np.std(redundancies):.3f}")
            print(f"    范围: [{np.min(redundancies):.3f}, {np.max(redundancies):.3f}]")
        print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='可视化NuScenes数据集冗余度分析结果'
    )
    parser.add_argument(
        '--result-path',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl',
        help='划分结果文件路径（.pkl或.json）'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split',
        help='可视化结果输出目录'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NuScenes数据集冗余度可视化")
    print("=" * 80)
    
    # 加载结果
    print(f"\n加载划分结果: {args.result_path}")
    split_result = load_split_result(args.result_path)
    
    # 打印统计信息
    print_statistics(split_result)
    
    # 生成可视化
    print("\n生成可视化图表...")
    os.makedirs(args.output_dir, exist_ok=True)
    
    plot_redundancy_distribution(split_result, args.output_dir)
    plot_velocity_histogram(split_result, args.output_dir)
    plot_redundancy_scatter(split_result, args.output_dir)
    plot_pie_charts(split_result, args.output_dir)
    
    print("\n" + "=" * 80)
    print("可视化完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()

