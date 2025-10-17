#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于数据冗余度对NuScenes数据集进行新的划分
冗余度通过车辆位移速率判断：速率低时冗余度高，速率高时冗余度低
"""

import json
import os
import numpy as np
from collections import defaultdict
import pickle
from typing import Dict, List, Tuple
import argparse


class NuScenesRedundancySplitter:
    """
    NuScenes数据集冗余度分析和划分器
    """
    
    def __init__(self, dataroot: str, version: str = 'v1.0-trainval'):
        """
        初始化数据集划分器
        
        Args:
            dataroot: NuScenes数据集根目录
            version: 数据集版本
        """
        self.dataroot = dataroot
        self.version = version
        self.version_path = os.path.join(dataroot, version)
        
        # 加载数据
        print(f"加载NuScenes数据集: {self.version_path}")
        self.sample = self._load_json('sample.json')
        self.scene = self._load_json('scene.json')
        self.sample_data = self._load_json('sample_data.json')
        self.ego_pose = self._load_json('ego_pose.json')
        
        # 创建索引
        self.sample_dict = {s['token']: s for s in self.sample}
        self.scene_dict = {s['token']: s for s in self.scene}
        self.ego_pose_dict = {e['token']: e for e in self.ego_pose}
        self.sample_data_dict = {sd['token']: sd for sd in self.sample_data}
        
    def _load_json(self, filename: str) -> List[Dict]:
        """加载JSON文件"""
        filepath = os.path.join(self.version_path, filename)
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def get_ego_pose_for_sample(self, sample_token: str) -> Dict:
        """
        获取sample对应的ego pose
        
        Args:
            sample_token: sample token
            
        Returns:
            ego_pose字典，包含translation和rotation
        """
        sample = self.sample_dict[sample_token]
        # 使用LIDAR_TOP的sample_data获取ego_pose
        lidar_token = sample['data']['LIDAR_TOP']
        sample_data = self.sample_data_dict[lidar_token]
        ego_pose_token = sample_data['ego_pose_token']
        return self.ego_pose_dict[ego_pose_token]
    
    def calculate_velocity(self, sample1_token: str, sample2_token: str) -> float:
        """
        计算两个连续sample之间的平均速率（米/秒）
        
        Args:
            sample1_token: 第一个sample的token
            sample2_token: 第二个sample的token
            
        Returns:
            速率（米/秒）
        """
        sample1 = self.sample_dict[sample1_token]
        sample2 = self.sample_dict[sample2_token]
        
        # 获取ego pose
        ego_pose1 = self.get_ego_pose_for_sample(sample1_token)
        ego_pose2 = self.get_ego_pose_for_sample(sample2_token)
        
        # 计算位置差
        pos1 = np.array(ego_pose1['translation'])
        pos2 = np.array(ego_pose2['translation'])
        distance = np.linalg.norm(pos2 - pos1)
        
        # 计算时间差（单位：秒）
        time1 = sample1['timestamp'] / 1e6  # 转换为秒
        time2 = sample2['timestamp'] / 1e6
        time_diff = time2 - time1
        
        if time_diff == 0:
            return 0.0
        
        # 速率 = 距离 / 时间
        velocity = distance / time_diff
        return velocity
    
    def calculate_redundancy_score(self, velocity: float, 
                                   low_threshold: float = 1.0,
                                   high_threshold: float = 5.0) -> float:
        """
        根据速率计算冗余度分数
        
        Args:
            velocity: 速率（米/秒）
            low_threshold: 低速阈值
            high_threshold: 高速阈值
            
        Returns:
            冗余度分数 [0, 1]，1表示最高冗余度
        """
        if velocity <= low_threshold:
            return 1.0
        elif velocity >= high_threshold:
            return 0.0
        else:
            # 线性插值
            return 1.0 - (velocity - low_threshold) / (high_threshold - low_threshold)
    
    def analyze_scene(self, scene_token: str, 
                     low_threshold: float = 1.0,
                     high_threshold: float = 5.0) -> Dict:
        """
        分析一个scene的冗余度
        
        Args:
            scene_token: scene token
            low_threshold: 低速阈值（米/秒）
            high_threshold: 高速阈值（米/秒）
            
        Returns:
            包含scene分析结果的字典
        """
        scene = self.scene_dict[scene_token]
        sample_token = scene['first_sample_token']
        
        velocities = []
        redundancy_scores = []
        sample_tokens = []
        
        # 遍历scene中的所有samples
        while sample_token:
            sample = self.sample_dict[sample_token]
            sample_tokens.append(sample_token)
            
            # 如果有下一个sample，计算速率
            if sample['next']:
                velocity = self.calculate_velocity(sample_token, sample['next'])
                redundancy = self.calculate_redundancy_score(
                    velocity, low_threshold, high_threshold
                )
                velocities.append(velocity)
                redundancy_scores.append(redundancy)
            
            sample_token = sample['next']
        
        result = {
            'scene_token': scene_token,
            'scene_name': scene['name'],
            'sample_tokens': sample_tokens,
            'velocities': velocities,
            'redundancy_scores': redundancy_scores,
            'avg_velocity': np.mean(velocities) if velocities else 0.0,
            'avg_redundancy': np.mean(redundancy_scores) if redundancy_scores else 0.0,
            'num_samples': len(sample_tokens)
        }
        
        return result
    
    def analyze_all_scenes(self, 
                          low_threshold: float = 1.0,
                          high_threshold: float = 5.0) -> List[Dict]:
        """
        分析所有scenes的冗余度
        
        Args:
            low_threshold: 低速阈值（米/秒）
            high_threshold: 高速阈值（米/秒）
            
        Returns:
            所有scenes的分析结果列表
        """
        print(f"\n开始分析所有scenes的冗余度...")
        print(f"低速阈值: {low_threshold} m/s")
        print(f"高速阈值: {high_threshold} m/s")
        
        results = []
        for i, scene in enumerate(self.scene):
            result = self.analyze_scene(
                scene['token'], low_threshold, high_threshold
            )
            results.append(result)
            
            if (i + 1) % 50 == 0:
                print(f"已分析 {i + 1}/{len(self.scene)} 个scenes")
        
        print(f"完成！共分析 {len(results)} 个scenes")
        return results
    
    def split_by_redundancy(self, 
                           analysis_results: List[Dict],
                           high_redundancy_threshold: float = 0.6,
                           low_redundancy_threshold: float = 0.3) -> Dict:
        """
        根据冗余度将数据分为高、中、低冗余度三类
        
        Args:
            analysis_results: 场景分析结果
            high_redundancy_threshold: 高冗余度阈值
            low_redundancy_threshold: 低冗余度阈值
            
        Returns:
            包含三类数据的字典
        """
        high_redundancy = []
        medium_redundancy = []
        low_redundancy = []
        
        for result in analysis_results:
            avg_redundancy = result['avg_redundancy']
            scene_info = {
                'scene_token': result['scene_token'],
                'scene_name': result['scene_name'],
                'sample_tokens': result['sample_tokens'],
                'avg_velocity': result['avg_velocity'],
                'avg_redundancy': result['avg_redundancy'],
                'num_samples': result['num_samples']
            }
            
            if avg_redundancy >= high_redundancy_threshold:
                high_redundancy.append(scene_info)
            elif avg_redundancy <= low_redundancy_threshold:
                low_redundancy.append(scene_info)
            else:
                medium_redundancy.append(scene_info)
        
        split_result = {
            'high_redundancy': high_redundancy,
            'medium_redundancy': medium_redundancy,
            'low_redundancy': low_redundancy
        }
        
        print(f"\n数据划分结果:")
        print(f"  高冗余度 (≥{high_redundancy_threshold}): {len(high_redundancy)} scenes, "
              f"{sum(s['num_samples'] for s in high_redundancy)} samples")
        print(f"  中冗余度 ({low_redundancy_threshold}-{high_redundancy_threshold}): "
              f"{len(medium_redundancy)} scenes, "
              f"{sum(s['num_samples'] for s in medium_redundancy)} samples")
        print(f"  低冗余度 (≤{low_redundancy_threshold}): {len(low_redundancy)} scenes, "
              f"{sum(s['num_samples'] for s in low_redundancy)} samples")
        
        return split_result
    
    def save_split(self, split_result: Dict, output_dir: str):
        """
        保存划分结果
        
        Args:
            split_result: 划分结果
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存为pickle格式
        pkl_path = os.path.join(output_dir, 'redundancy_split.pkl')
        with open(pkl_path, 'wb') as f:
            pickle.dump(split_result, f)
        print(f"\n已保存pickle格式: {pkl_path}")
        
        # 保存为JSON格式（可读性更好）
        json_path = os.path.join(output_dir, 'redundancy_split.json')
        with open(json_path, 'w') as f:
            json.dump(split_result, f, indent=2)
        print(f"已保存JSON格式: {json_path}")
        
        # 保存每个类别的sample token列表
        for category in ['high_redundancy', 'medium_redundancy', 'low_redundancy']:
            sample_tokens = []
            for scene_info in split_result[category]:
                sample_tokens.extend(scene_info['sample_tokens'])
            
            token_path = os.path.join(output_dir, f'{category}_sample_tokens.txt')
            with open(token_path, 'w') as f:
                for token in sample_tokens:
                    f.write(f"{token}\n")
            print(f"已保存sample tokens: {token_path} ({len(sample_tokens)} samples)")
        
        # 生成统计报告
        self._generate_report(split_result, output_dir)
    
    def _generate_report(self, split_result: Dict, output_dir: str):
        """生成统计报告"""
        report_path = os.path.join(output_dir, 'redundancy_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("NuScenes数据集冗余度分析报告\n")
            f.write("=" * 80 + "\n\n")
            
            total_scenes = sum(len(split_result[k]) for k in split_result)
            total_samples = sum(
                sum(s['num_samples'] for s in split_result[k]) 
                for k in split_result
            )
            
            f.write(f"总计: {total_scenes} scenes, {total_samples} samples\n\n")
            
            categories = {
                'high_redundancy': '高冗余度',
                'medium_redundancy': '中冗余度',
                'low_redundancy': '低冗余度'
            }
            
            for key, name in categories.items():
                scenes = split_result[key]
                num_scenes = len(scenes)
                num_samples = sum(s['num_samples'] for s in scenes)
                avg_vel = np.mean([s['avg_velocity'] for s in scenes]) if scenes else 0
                avg_red = np.mean([s['avg_redundancy'] for s in scenes]) if scenes else 0
                
                f.write(f"\n{name}:\n")
                f.write(f"  Scenes数量: {num_scenes} ({num_scenes/total_scenes*100:.1f}%)\n")
                f.write(f"  Samples数量: {num_samples} ({num_samples/total_samples*100:.1f}%)\n")
                f.write(f"  平均速率: {avg_vel:.2f} m/s\n")
                f.write(f"  平均冗余度: {avg_red:.3f}\n")
                
                if scenes:
                    f.write(f"\n  前10个scenes:\n")
                    for i, scene in enumerate(scenes[:10]):
                        f.write(f"    {i+1}. {scene['scene_name']}: "
                               f"速率={scene['avg_velocity']:.2f} m/s, "
                               f"冗余度={scene['avg_redundancy']:.3f}, "
                               f"samples={scene['num_samples']}\n")
        
        print(f"已生成统计报告: {report_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='基于数据冗余度对NuScenes数据集进行新的划分'
    )
    parser.add_argument(
        '--dataroot',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes',
        help='NuScenes数据集根目录'
    )
    parser.add_argument(
        '--version',
        type=str,
        default='v1.0-trainval',
        help='数据集版本'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split',
        help='输出目录'
    )
    parser.add_argument(
        '--low-velocity',
        type=float,
        default=1.0,
        help='低速阈值（米/秒），低于此速度认为冗余度高'
    )
    parser.add_argument(
        '--high-velocity',
        type=float,
        default=5.0,
        help='高速阈值（米/秒），高于此速度认为冗余度低'
    )
    parser.add_argument(
        '--high-redundancy-threshold',
        type=float,
        default=0.6,
        help='高冗余度分类阈值'
    )
    parser.add_argument(
        '--low-redundancy-threshold',
        type=float,
        default=0.3,
        help='低冗余度分类阈值'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NuScenes数据集冗余度分析与划分")
    print("=" * 80)
    
    # 初始化splitter
    splitter = NuScenesRedundancySplitter(args.dataroot, args.version)
    
    # 分析所有scenes
    analysis_results = splitter.analyze_all_scenes(
        low_threshold=args.low_velocity,
        high_threshold=args.high_velocity
    )
    
    # 根据冗余度进行划分
    split_result = splitter.split_by_redundancy(
        analysis_results,
        high_redundancy_threshold=args.high_redundancy_threshold,
        low_redundancy_threshold=args.low_redundancy_threshold
    )
    
    # 保存结果
    splitter.save_split(split_result, args.output_dir)
    
    print("\n" + "=" * 80)
    print("划分完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()

