#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冗余度划分结果的工具函数
提供便捷的接口来加载和使用划分结果
"""

import pickle
import json
import os
from typing import List, Dict, Set, Optional
import numpy as np


class RedundancySplitLoader:
    """
    冗余度划分结果加载器
    提供方便的API来访问和使用划分结果
    """
    
    def __init__(self, split_path: str):
        """
        初始化加载器
        
        Args:
            split_path: 划分结果文件路径（.pkl或.json）
        """
        self.split_path = split_path
        self.split_result = self._load_split()
        self._build_indices()
    
    def _load_split(self) -> Dict:
        """加载划分结果"""
        if self.split_path.endswith('.pkl'):
            with open(self.split_path, 'rb') as f:
                return pickle.load(f)
        elif self.split_path.endswith('.json'):
            with open(self.split_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError("不支持的文件格式，请使用.pkl或.json文件")
    
    def _build_indices(self):
        """构建索引以便快速查询"""
        # 场景token到类别的映射
        self.scene_to_category = {}
        
        # 样本token到类别的映射
        self.sample_to_category = {}
        
        # 场景token到场景信息的映射
        self.scene_info_dict = {}
        
        for category in ['high_redundancy', 'medium_redundancy', 'low_redundancy']:
            for scene_info in self.split_result[category]:
                scene_token = scene_info['scene_token']
                self.scene_to_category[scene_token] = category
                self.scene_info_dict[scene_token] = scene_info
                
                for sample_token in scene_info['sample_tokens']:
                    self.sample_to_category[sample_token] = category
    
    def get_category_by_sample(self, sample_token: str) -> Optional[str]:
        """
        根据sample token获取其所属的冗余度类别
        
        Args:
            sample_token: sample token
            
        Returns:
            类别名称 ('high_redundancy', 'medium_redundancy', 'low_redundancy')
            如果找不到返回None
        """
        return self.sample_to_category.get(sample_token)
    
    def get_category_by_scene(self, scene_token: str) -> Optional[str]:
        """
        根据scene token获取其所属的冗余度类别
        
        Args:
            scene_token: scene token
            
        Returns:
            类别名称，如果找不到返回None
        """
        return self.scene_to_category.get(scene_token)
    
    def get_scene_info(self, scene_token: str) -> Optional[Dict]:
        """
        获取场景的详细信息
        
        Args:
            scene_token: scene token
            
        Returns:
            场景信息字典，如果找不到返回None
        """
        return self.scene_info_dict.get(scene_token)
    
    def get_samples_by_category(self, category: str) -> List[str]:
        """
        获取指定类别的所有sample tokens
        
        Args:
            category: 类别名称 ('high_redundancy', 'medium_redundancy', 'low_redundancy')
            
        Returns:
            sample token列表
        """
        sample_tokens = []
        for scene_info in self.split_result[category]:
            sample_tokens.extend(scene_info['sample_tokens'])
        return sample_tokens
    
    def get_scenes_by_category(self, category: str) -> List[Dict]:
        """
        获取指定类别的所有场景信息
        
        Args:
            category: 类别名称
            
        Returns:
            场景信息列表
        """
        return self.split_result[category]
    
    def sample_from_category(self, category: str, n: int, 
                            random_state: Optional[int] = None) -> List[str]:
        """
        从指定类别中随机采样样本
        
        Args:
            category: 类别名称
            n: 采样数量
            random_state: 随机种子
            
        Returns:
            采样得到的sample token列表
        """
        sample_tokens = self.get_samples_by_category(category)
        
        if random_state is not None:
            np.random.seed(random_state)
        
        n = min(n, len(sample_tokens))
        indices = np.random.choice(len(sample_tokens), n, replace=False)
        
        return [sample_tokens[i] for i in indices]
    
    def get_balanced_split(self, train_ratio: float = 0.7, val_ratio: float = 0.15,
                          test_ratio: float = 0.15, random_state: Optional[int] = None,
                          by_scene: bool = True) -> Dict[str, List[str]]:
        """
        创建平衡的训练/验证/测试划分
        在每个冗余度类别中按比例划分
        
        Args:
            train_ratio: 训练集比例
            val_ratio: 验证集比例
            test_ratio: 测试集比例
            random_state: 随机种子
            by_scene: 是否按场景划分（True）还是按样本划分（False）
            
        Returns:
            包含'train', 'val', 'test'键的字典，值为sample token列表
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, \
            "比例之和必须为1"
        
        if random_state is not None:
            np.random.seed(random_state)
        
        train_samples = []
        val_samples = []
        test_samples = []
        
        for category in ['high_redundancy', 'medium_redundancy', 'low_redundancy']:
            if by_scene:
                # 按场景划分
                scenes = self.split_result[category]
                n_scenes = len(scenes)
                
                # 随机打乱场景
                indices = np.random.permutation(n_scenes)
                
                n_train = int(n_scenes * train_ratio)
                n_val = int(n_scenes * val_ratio)
                
                train_indices = indices[:n_train]
                val_indices = indices[n_train:n_train + n_val]
                test_indices = indices[n_train + n_val:]
                
                # 收集样本
                for idx in train_indices:
                    train_samples.extend(scenes[idx]['sample_tokens'])
                for idx in val_indices:
                    val_samples.extend(scenes[idx]['sample_tokens'])
                for idx in test_indices:
                    test_samples.extend(scenes[idx]['sample_tokens'])
            else:
                # 按样本划分
                samples = self.get_samples_by_category(category)
                n_samples = len(samples)
                
                # 随机打乱样本
                indices = np.random.permutation(n_samples)
                
                n_train = int(n_samples * train_ratio)
                n_val = int(n_samples * val_ratio)
                
                train_samples.extend([samples[i] for i in indices[:n_train]])
                val_samples.extend([samples[i] for i in indices[n_train:n_train + n_val]])
                test_samples.extend([samples[i] for i in indices[n_train + n_val:]])
        
        return {
            'train': train_samples,
            'val': val_samples,
            'test': test_samples
        }
    
    def get_low_redundancy_subset(self, ratio: float = 0.5,
                                  random_state: Optional[int] = None) -> List[str]:
        """
        获取低冗余度子集
        主要从低冗余度类别采样，可包含部分中冗余度数据
        
        Args:
            ratio: 从低冗余度类别采样的比例
            random_state: 随机种子
            
        Returns:
            sample token列表
        """
        if random_state is not None:
            np.random.seed(random_state)
        
        # 获取所有低冗余度样本
        low_samples = self.get_samples_by_category('low_redundancy')
        
        # 从中冗余度采样
        medium_samples = self.get_samples_by_category('medium_redundancy')
        n_medium = int(len(low_samples) * (1 - ratio))
        
        if n_medium > 0 and medium_samples:
            medium_indices = np.random.choice(len(medium_samples), 
                                            min(n_medium, len(medium_samples)),
                                            replace=False)
            selected_medium = [medium_samples[i] for i in medium_indices]
        else:
            selected_medium = []
        
        return low_samples + selected_medium
    
    def get_statistics(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            包含各类别统计信息的字典
        """
        stats = {}
        
        for category in ['high_redundancy', 'medium_redundancy', 'low_redundancy']:
            scenes = self.split_result[category]
            sample_tokens = self.get_samples_by_category(category)
            
            velocities = [s['avg_velocity'] for s in scenes]
            redundancies = [s['avg_redundancy'] for s in scenes]
            
            stats[category] = {
                'num_scenes': len(scenes),
                'num_samples': len(sample_tokens),
                'velocity_stats': {
                    'mean': float(np.mean(velocities)) if velocities else 0,
                    'median': float(np.median(velocities)) if velocities else 0,
                    'std': float(np.std(velocities)) if velocities else 0,
                    'min': float(np.min(velocities)) if velocities else 0,
                    'max': float(np.max(velocities)) if velocities else 0,
                },
                'redundancy_stats': {
                    'mean': float(np.mean(redundancies)) if redundancies else 0,
                    'median': float(np.median(redundancies)) if redundancies else 0,
                    'std': float(np.std(redundancies)) if redundancies else 0,
                    'min': float(np.min(redundancies)) if redundancies else 0,
                    'max': float(np.max(redundancies)) if redundancies else 0,
                }
            }
        
        return stats
    
    def print_summary(self):
        """打印摘要信息"""
        print("=" * 80)
        print("冗余度划分摘要")
        print("=" * 80)
        
        stats = self.get_statistics()
        
        category_names = {
            'high_redundancy': '高冗余度',
            'medium_redundancy': '中冗余度',
            'low_redundancy': '低冗余度'
        }
        
        for category, name in category_names.items():
            s = stats[category]
            print(f"\n{name}:")
            print(f"  场景数: {s['num_scenes']}")
            print(f"  样本数: {s['num_samples']}")
            print(f"  平均速率: {s['velocity_stats']['mean']:.2f} m/s")
            print(f"  平均冗余度: {s['redundancy_stats']['mean']:.3f}")


def load_redundancy_split(split_path: str) -> RedundancySplitLoader:
    """
    便捷函数：加载冗余度划分结果
    
    Args:
        split_path: 划分结果文件路径
        
    Returns:
        RedundancySplitLoader实例
    """
    return RedundancySplitLoader(split_path)


# 使用示例
if __name__ == '__main__':
    # 加载划分结果
    loader = load_redundancy_split(
        '/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl'
    )
    
    # 打印摘要
    loader.print_summary()
    
    # 示例：获取低冗余度样本
    print("\n" + "=" * 80)
    print("示例用法")
    print("=" * 80)
    
    low_red_samples = loader.get_samples_by_category('low_redundancy')
    print(f"\n低冗余度样本数: {len(low_red_samples)}")
    print(f"前5个样本token: {low_red_samples[:5]}")
    
    # 示例：创建平衡划分
    split = loader.get_balanced_split(
        train_ratio=0.7, val_ratio=0.15, test_ratio=0.15,
        random_state=42, by_scene=True
    )
    print(f"\n平衡划分:")
    print(f"  训练集: {len(split['train'])} samples")
    print(f"  验证集: {len(split['val'])} samples")
    print(f"  测试集: {len(split['test'])} samples")
    
    # 示例：查询样本所属类别
    if low_red_samples:
        sample_token = low_red_samples[0]
        category = loader.get_category_by_sample(sample_token)
        print(f"\n样本 {sample_token[:10]}... 属于: {category}")

