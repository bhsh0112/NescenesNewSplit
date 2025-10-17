#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualize NuScenes dataset redundancy analysis results
"""

import pickle
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
import argparse

# Set font
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
rcParams['axes.unicode_minus'] = False


def load_split_result(result_path: str):
    """
    Load split result
    
    Args:
        result_path: Result file path (pkl or json)
        
    Returns:
        Split result dictionary
    """
    if result_path.endswith('.pkl'):
        with open(result_path, 'rb') as f:
            return pickle.load(f)
    elif result_path.endswith('.json'):
        with open(result_path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError("Unsupported file format, please use .pkl or .json file")


def plot_redundancy_distribution(split_result: dict, output_dir: str):
    """
    Plot redundancy distribution
    
    Args:
        split_result: Split result
        output_dir: Output directory
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('NuScenes Dataset Redundancy Analysis', fontsize=16, fontweight='bold')
    
    # 1. Scene count distribution by category
    ax1 = axes[0, 0]
    categories = ['High Redundancy', 'Medium Redundancy', 'Low Redundancy']
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    scene_counts = [len(split_result[k]) for k in keys]
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    bars = ax1.bar(categories, scene_counts, color=colors, alpha=0.7, edgecolor='black')
    ax1.set_ylabel('Number of Scenes', fontsize=12)
    ax1.set_title('Scene Count Distribution by Category', fontsize=13, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3)
    
    # Add count labels on bars
    for bar, count in zip(bars, scene_counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 2. Sample count distribution by category
    ax2 = axes[0, 1]
    sample_counts = [sum(s['num_samples'] for s in split_result[k]) for k in keys]
    
    bars = ax2.bar(categories, sample_counts, color=colors, alpha=0.7, edgecolor='black')
    ax2.set_ylabel('Number of Samples', fontsize=12)
    ax2.set_title('Sample Count Distribution by Category', fontsize=13, fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    for bar, count in zip(bars, sample_counts):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{count}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # 3. Average velocity distribution
    ax3 = axes[1, 0]
    velocities_by_category = []
    for key in keys:
        velocities = [s['avg_velocity'] for s in split_result[key]]
        velocities_by_category.append(velocities)
    
    bp = ax3.boxplot(velocities_by_category, tick_labels=categories, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax3.set_ylabel('Average Velocity (m/s)', fontsize=12)
    ax3.set_title('Velocity Distribution by Category', fontsize=13, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Redundancy score distribution
    ax4 = axes[1, 1]
    redundancies_by_category = []
    for key in keys:
        redundancies = [s['avg_redundancy'] for s in split_result[key]]
        redundancies_by_category.append(redundancies)
    
    bp = ax4.boxplot(redundancies_by_category, tick_labels=categories, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    
    ax4.set_ylabel('Redundancy Score', fontsize=12)
    ax4.set_title('Redundancy Distribution by Category', fontsize=13, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'redundancy_distribution.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved distribution plot: {output_path}")
    plt.close()


def plot_velocity_histogram(split_result: dict, output_dir: str):
    """
    Plot velocity histogram
    
    Args:
        split_result: Split result
        output_dir: Output directory
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['High Redundancy', 'Medium Redundancy', 'Low Redundancy']
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    all_velocities = []
    for key, label, color in zip(keys, labels, colors):
        velocities = [s['avg_velocity'] for s in split_result[key]]
        all_velocities.extend(velocities)
        ax.hist(velocities, bins=30, alpha=0.6, label=label, color=color, edgecolor='black')
    
    ax.set_xlabel('Average Velocity (m/s)', fontsize=12)
    ax.set_ylabel('Number of Scenes', fontsize=12)
    ax.set_title('Velocity Distribution Histogram by Category', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'velocity_histogram.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved velocity histogram: {output_path}")
    plt.close()


def plot_redundancy_scatter(split_result: dict, output_dir: str):
    """
    Plot velocity-redundancy scatter plot
    
    Args:
        split_result: Split result
        output_dir: Output directory
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['High Redundancy', 'Medium Redundancy', 'Low Redundancy']
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    for key, label, color in zip(keys, labels, colors):
        velocities = [s['avg_velocity'] for s in split_result[key]]
        redundancies = [s['avg_redundancy'] for s in split_result[key]]
        sizes = [s['num_samples'] for s in split_result[key]]
        
        # Normalize size for visualization
        sizes_normalized = [s * 2 for s in sizes]
        
        ax.scatter(velocities, redundancies, s=sizes_normalized, alpha=0.6,
                  label=label, color=color, edgecolors='black', linewidth=0.5)
    
    ax.set_xlabel('Average Velocity (m/s)', fontsize=12)
    ax.set_ylabel('Redundancy Score', fontsize=12)
    ax.set_title('Velocity-Redundancy Relationship\n(Bubble size indicates sample count)', 
                fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'redundancy_scatter.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved scatter plot: {output_path}")
    plt.close()


def plot_pie_charts(split_result: dict, output_dir: str):
    """
    Plot pie charts
    
    Args:
        split_result: Split result
        output_dir: Output directory
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['High Redundancy', 'Medium Redundancy', 'Low Redundancy']
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f']
    
    # Scene count pie chart
    scene_counts = [len(split_result[k]) for k in keys]
    axes[0].pie(scene_counts, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11})
    axes[0].set_title('Scene Count Distribution', fontsize=13, fontweight='bold')
    
    # Sample count pie chart
    sample_counts = [sum(s['num_samples'] for s in split_result[k]) for k in keys]
    axes[1].pie(sample_counts, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 11})
    axes[1].set_title('Sample Count Distribution', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, 'redundancy_pie_charts.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved pie charts: {output_path}")
    plt.close()


def print_statistics(split_result: dict):
    """
    Print statistics
    
    Args:
        split_result: Split result
    """
    print("\n" + "=" * 80)
    print("Dataset Split Statistics")
    print("=" * 80)
    
    keys = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
    labels = ['High Redundancy', 'Medium Redundancy', 'Low Redundancy']
    
    total_scenes = sum(len(split_result[k]) for k in keys)
    total_samples = sum(sum(s['num_samples'] for s in split_result[k]) for k in keys)
    
    print(f"\nTotal: {total_scenes} scenes, {total_samples} samples\n")
    
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
            print(f"  Velocity Stats:")
            print(f"    Mean: {np.mean(velocities):.2f} m/s")
            print(f"    Median: {np.median(velocities):.2f} m/s")
            print(f"    Std: {np.std(velocities):.2f} m/s")
            print(f"    Range: [{np.min(velocities):.2f}, {np.max(velocities):.2f}] m/s")
        
        if redundancies:
            print(f"  Redundancy Stats:")
            print(f"    Mean: {np.mean(redundancies):.3f}")
            print(f"    Median: {np.median(redundancies):.3f}")
            print(f"    Std: {np.std(redundancies):.3f}")
            print(f"    Range: [{np.min(redundancies):.3f}, {np.max(redundancies):.3f}]")
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Visualize NuScenes dataset redundancy analysis results'
    )
    parser.add_argument(
        '--result-path',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl',
        help='Split result file path (.pkl or .json)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split',
        help='Visualization output directory'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NuScenes Dataset Redundancy Visualization")
    print("=" * 80)
    
    # Load result
    print(f"\nLoading split result: {args.result_path}")
    split_result = load_split_result(args.result_path)
    
    # Print statistics
    print_statistics(split_result)
    
    # Generate visualizations
    print("\nGenerating visualization plots...")
    os.makedirs(args.output_dir, exist_ok=True)
    
    plot_redundancy_distribution(split_result, args.output_dir)
    plot_velocity_histogram(split_result, args.output_dir)
    plot_redundancy_scatter(split_result, args.output_dir)
    plot_pie_charts(split_result, args.output_dir)
    
    print("\n" + "=" * 80)
    print("Visualization completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()

