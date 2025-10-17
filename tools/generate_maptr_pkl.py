#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MapTR pkl索引生成器
根据冗余度划分结果生成MapTR训练所需的pkl索引文件
"""

import pickle
import os
import argparse
from typing import List, Dict, Optional, Set
import numpy as np
from redundancy_utils import RedundancySplitLoader


class MapTRPklGenerator:
    """
    MapTR pkl索引生成器
    根据冗余度划分结果生成MapTR训练用的pkl索引文件
    """
    
    def __init__(self, redundancy_split_path: str, 
                 maptr_data_root: str = None):
        """
        初始化适配器
        
        Args:
            redundancy_split_path: 冗余度划分结果路径
            maptr_data_root: MapTR数据根目录（可选）
        """
        self.loader = RedundancySplitLoader(redundancy_split_path)
        self.maptr_data_root = maptr_data_root
        
    def filter_info_by_tokens(self, 
                              original_info_path: str,
                              target_tokens: Set[str],
                              output_path: str):
        """
        根据token列表过滤原始info文件
        
        Args:
            original_info_path: 原始的MapTR info pkl文件路径
            target_tokens: 目标sample token集合
            output_path: 输出路径
        """
        print(f"加载原始info文件: {original_info_path}")
        with open(original_info_path, 'rb') as f:
            original_data = pickle.load(f)
        
        # 提取metadata
        metadata = original_data.get('metadata', {})
        original_infos = original_data['infos']
        
        print(f"原始样本数: {len(original_infos)}")
        
        # 过滤样本
        filtered_infos = []
        for info in original_infos:
            # MapTR的info格式中，sample token存储在'token'字段
            if info.get('token') in target_tokens:
                filtered_infos.append(info)
        
        print(f"过滤后样本数: {len(filtered_infos)}")
        
        # 构造输出数据
        output_data = {
            'infos': filtered_infos,
            'metadata': metadata
        }
        
        # 保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'wb') as f:
            pickle.dump(output_data, f)
        
        print(f"已保存到: {output_path}")
        
        return len(filtered_infos)
    
    def create_low_redundancy_split(self,
                                   original_train_path: str,
                                   original_val_path: str,
                                   output_dir: str,
                                   include_categories: List[str] = ['low_redundancy']):
        """
        创建低冗余度划分的MapTR数据
        
        Args:
            original_train_path: 原始训练集info文件
            original_val_path: 原始验证集info文件
            output_dir: 输出目录
            include_categories: 包含的冗余度类别
        """
        print("\n" + "=" * 80)
        print("创建低冗余度MapTR数据划分")
        print("=" * 80)
        
        # 获取目标tokens
        target_tokens = set()
        for category in include_categories:
            tokens = self.loader.get_samples_by_category(category)
            target_tokens.update(tokens)
            print(f"\n{category}: {len(tokens)} samples")
        
        print(f"\n总计目标样本数: {len(target_tokens)}")
        
        # 过滤训练集
        print("\n处理训练集...")
        train_output_path = os.path.join(output_dir, 'nuscenes_infos_temporal_train.pkl')
        train_count = self.filter_info_by_tokens(
            original_train_path, target_tokens, train_output_path
        )
        
        # 过滤验证集
        print("\n处理验证集...")
        val_output_path = os.path.join(output_dir, 'nuscenes_infos_temporal_val.pkl')
        val_count = self.filter_info_by_tokens(
            original_val_path, target_tokens, val_output_path
        )
        
        # 生成统计报告
        report_path = os.path.join(output_dir, 'maptr_split_report.txt')
        self._generate_report(
            report_path, include_categories, train_count, val_count
        )
        
        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)
        
        return {
            'train_path': train_output_path,
            'val_path': val_output_path,
            'train_count': train_count,
            'val_count': val_count
        }
    
    def create_custom_split(self,
                           original_train_path: str,
                           original_val_path: str,
                           output_dir: str,
                           low_ratio: float = 1.0,
                           medium_ratio: float = 0.0,
                           high_ratio: float = 0.0,
                           random_state: int = 42):
        """
        创建自定义比例的数据划分
        
        Args:
            original_train_path: 原始训练集info文件
            original_val_path: 原始验证集info文件
            output_dir: 输出目录
            low_ratio: 低冗余度样本采样比例
            medium_ratio: 中冗余度样本采样比例
            high_ratio: 高冗余度样本采样比例
            random_state: 随机种子
        """
        print("\n" + "=" * 80)
        print("创建自定义比例MapTR数据划分")
        print("=" * 80)
        print(f"\n配置:")
        print(f"  低冗余度比例: {low_ratio:.1%}")
        print(f"  中冗余度比例: {medium_ratio:.1%}")
        print(f"  高冗余度比例: {high_ratio:.1%}")
        
        np.random.seed(random_state)
        
        # 采样各类别
        target_tokens = set()
        
        categories = {
            'low_redundancy': low_ratio,
            'medium_redundancy': medium_ratio,
            'high_redundancy': high_ratio
        }
        
        for category, ratio in categories.items():
            all_tokens = self.loader.get_samples_by_category(category)
            
            if ratio >= 1.0:
                selected_tokens = all_tokens
            elif ratio > 0:
                n_samples = int(len(all_tokens) * ratio)
                indices = np.random.choice(len(all_tokens), n_samples, replace=False)
                selected_tokens = [all_tokens[i] for i in indices]
            else:
                selected_tokens = []
            
            target_tokens.update(selected_tokens)
            print(f"\n{category}:")
            print(f"  总数: {len(all_tokens)}")
            print(f"  选择: {len(selected_tokens)}")
        
        print(f"\n总计目标样本数: {len(target_tokens)}")
        
        # 过滤训练集和验证集
        print("\n处理训练集...")
        train_output_path = os.path.join(output_dir, 'nuscenes_infos_temporal_train.pkl')
        train_count = self.filter_info_by_tokens(
            original_train_path, target_tokens, train_output_path
        )
        
        print("\n处理验证集...")
        val_output_path = os.path.join(output_dir, 'nuscenes_infos_temporal_val.pkl')
        val_count = self.filter_info_by_tokens(
            original_val_path, target_tokens, val_output_path
        )
        
        # 生成报告
        report_path = os.path.join(output_dir, 'maptr_split_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MapTR自定义划分报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"低冗余度比例: {low_ratio:.1%}\n")
            f.write(f"中冗余度比例: {medium_ratio:.1%}\n")
            f.write(f"高冗余度比例: {high_ratio:.1%}\n\n")
            f.write(f"训练集样本数: {train_count}\n")
            f.write(f"验证集样本数: {val_count}\n")
            f.write(f"总计: {train_count + val_count}\n")
        
        print(f"\n已生成报告: {report_path}")
        
        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)
        
        return {
            'train_path': train_output_path,
            'val_path': val_output_path,
            'train_count': train_count,
            'val_count': val_count
        }
    
    def create_balanced_redundancy_split(self,
                                        original_train_path: str,
                                        original_val_path: str,
                                        output_dir: str):
        """
        创建各冗余度类别平衡的划分
        从每个类别取相同数量的样本
        
        Args:
            original_train_path: 原始训练集info文件
            original_val_path: 原始验证集info文件
            output_dir: 输出目录
        """
        print("\n" + "=" * 80)
        print("创建平衡冗余度MapTR数据划分")
        print("=" * 80)
        
        # 找到最小类别的样本数
        categories = ['high_redundancy', 'medium_redundancy', 'low_redundancy']
        category_counts = {}
        
        for category in categories:
            tokens = self.loader.get_samples_by_category(category)
            category_counts[category] = len(tokens)
            print(f"{category}: {len(tokens)} samples")
        
        # 使用最小数量作为平衡基准
        min_count = min(category_counts.values())
        print(f"\n平衡基准（最小类别样本数）: {min_count}")
        
        # 从每个类别采样相同数量
        target_tokens = set()
        for category in categories:
            tokens = self.loader.sample_from_category(
                category, n=min_count, random_state=42
            )
            target_tokens.update(tokens)
            print(f"从{category}采样: {len(tokens)}")
        
        print(f"\n总计样本数: {len(target_tokens)}")
        
        # 过滤数据
        print("\n处理训练集...")
        train_output_path = os.path.join(output_dir, 'nuscenes_infos_temporal_train.pkl')
        train_count = self.filter_info_by_tokens(
            original_train_path, target_tokens, train_output_path
        )
        
        print("\n处理验证集...")
        val_output_path = os.path.join(output_dir, 'nuscenes_infos_temporal_val.pkl')
        val_count = self.filter_info_by_tokens(
            original_val_path, target_tokens, val_output_path
        )
        
        # 生成报告
        report_path = os.path.join(output_dir, 'maptr_split_report.txt')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MapTR平衡冗余度划分报告\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"每个类别采样数: {min_count}\n\n")
            f.write(f"训练集样本数: {train_count}\n")
            f.write(f"验证集样本数: {val_count}\n")
            f.write(f"总计: {train_count + val_count}\n")
        
        print(f"\n已生成报告: {report_path}")
        
        print("\n" + "=" * 80)
        print("完成！")
        print("=" * 80)
        
        return {
            'train_path': train_output_path,
            'val_path': val_output_path,
            'train_count': train_count,
            'val_count': val_count
        }
    
    def _generate_report(self, report_path: str, categories: List[str],
                        train_count: int, val_count: int):
        """生成报告"""
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MapTR数据划分报告\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("包含的冗余度类别:\n")
            for category in categories:
                tokens = self.loader.get_samples_by_category(category)
                f.write(f"  - {category}: {len(tokens)} samples\n")
            
            f.write(f"\n训练集样本数: {train_count}\n")
            f.write(f"验证集样本数: {val_count}\n")
            f.write(f"总计: {train_count + val_count}\n")
        
        print(f"\n已生成报告: {report_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='将冗余度划分结果适配到MapTR数据格式'
    )
    
    parser.add_argument(
        '--redundancy-split',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl',
        help='冗余度划分结果文件路径'
    )
    
    parser.add_argument(
        '--original-train',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes/nuscenes_infos_temporal_train.pkl',
        help='原始MapTR训练集info文件路径'
    )
    
    parser.add_argument(
        '--original-val',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes/nuscenes_infos_temporal_val.pkl',
        help='原始MapTR验证集info文件路径'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy',
        help='输出目录'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        default='low_only',
        choices=['low_only', 'custom', 'balanced'],
        help='划分模式：low_only(仅低冗余度), custom(自定义比例), balanced(平衡各类)'
    )
    
    parser.add_argument(
        '--low-ratio',
        type=float,
        default=1.0,
        help='自定义模式：低冗余度比例'
    )
    
    parser.add_argument(
        '--medium-ratio',
        type=float,
        default=0.0,
        help='自定义模式：中冗余度比例'
    )
    
    parser.add_argument(
        '--high-ratio',
        type=float,
        default=0.0,
        help='自定义模式：高冗余度比例'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("MapTR pkl索引生成器")
    print("=" * 80)
    
    # 检查文件是否存在
    if not os.path.exists(args.redundancy_split):
        print(f"\n错误: 找不到冗余度划分文件: {args.redundancy_split}")
        print("请先运行 split_by_redundancy.py 生成冗余度划分")
        return
    
    if not os.path.exists(args.original_train):
        print(f"\n错误: 找不到原始训练集文件: {args.original_train}")
        print("请确保MapTR数据已准备好")
        return
    
    if not os.path.exists(args.original_val):
        print(f"\n错误: 找不到原始验证集文件: {args.original_val}")
        print("请确保MapTR数据已准备好")
        return
    
    # 创建生成器
    generator = MapTRPklGenerator(args.redundancy_split)
    
    # 根据模式执行
    if args.mode == 'low_only':
        result = generator.create_low_redundancy_split(
            args.original_train,
            args.original_val,
            args.output_dir,
            include_categories=['low_redundancy']
        )
    elif args.mode == 'custom':
        result = generator.create_custom_split(
            args.original_train,
            args.original_val,
            args.output_dir,
            low_ratio=args.low_ratio,
            medium_ratio=args.medium_ratio,
            high_ratio=args.high_ratio
        )
    elif args.mode == 'balanced':
        result = generator.create_balanced_redundancy_split(
            args.original_train,
            args.original_val,
            args.output_dir
        )
    
    print(f"\n生成的文件:")
    print(f"  训练集: {result['train_path']} ({result['train_count']} samples)")
    print(f"  验证集: {result['val_path']} ({result['val_count']} samples)")
    print(f"\n使用方法:")
    print(f"  在MapTR配置文件中，将数据路径指向: {args.output_dir}")


if __name__ == '__main__':
    main()

