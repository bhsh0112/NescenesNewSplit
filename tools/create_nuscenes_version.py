#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建完整的NuScenes版本（基于冗余度划分）
生成新的v1.0-xxx目录，包含所有元数据和数据文件
"""

import json
import os
import shutil
import argparse
from typing import Set, Dict, List
from collections import defaultdict
from redundancy_utils import RedundancySplitLoader


class NuScenesVersionCreator:
    """
    创建新的NuScenes版本
    """
    
    def __init__(self, 
                 original_dataroot: str,
                 original_version: str,
                 redundancy_split_path: str):
        """
        初始化
        
        Args:
            original_dataroot: 原始NuScenes数据根目录
            original_version: 原始版本名称（如v1.0-trainval）
            redundancy_split_path: 冗余度划分结果路径
        """
        self.original_dataroot = original_dataroot
        self.original_version = original_version
        self.original_version_path = os.path.join(original_dataroot, original_version)
        
        # 加载冗余度划分
        self.redundancy_loader = RedundancySplitLoader(redundancy_split_path)
        
        print(f"原始数据路径: {self.original_version_path}")
        
    def _load_json(self, filename: str) -> List[Dict]:
        """加载JSON文件"""
        filepath = os.path.join(self.original_version_path, filename)
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _save_json(self, data: List[Dict], filepath: str):
        """保存JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f)
        print(f"  已保存: {os.path.basename(filepath)} ({len(data)} 条记录)")
    
    def create_version(self,
                      output_dataroot: str,
                      version_name: str,
                      categories: List[str],
                      use_symlink: bool = True):
        """
        创建新的NuScenes版本
        
        Args:
            output_dataroot: 输出数据根目录
            version_name: 新版本名称（如v1.0-low-redundancy）
            categories: 包含的冗余度类别列表
            use_symlink: 是否使用符号链接（节省空间）
        """
        print("\n" + "=" * 80)
        print(f"创建NuScenes版本: {version_name}")
        print("=" * 80)
        
        output_version_path = os.path.join(output_dataroot, version_name)
        os.makedirs(output_version_path, exist_ok=True)
        
        # 获取目标sample tokens
        target_tokens = set()
        for category in categories:
            tokens = self.redundancy_loader.get_samples_by_category(category)
            target_tokens.update(tokens)
        
        print(f"\n目标样本数: {len(target_tokens)}")
        print(f"类别: {', '.join(categories)}")
        
        # 加载原始数据
        print("\n加载原始数据...")
        sample_list = self._load_json('sample.json')
        scene_list = self._load_json('scene.json')
        sample_data_list = self._load_json('sample_data.json')
        ego_pose_list = self._load_json('ego_pose.json')
        calibrated_sensor_list = self._load_json('calibrated_sensor.json')
        sensor_list = self._load_json('sensor.json')
        log_list = self._load_json('log.json')
        
        # 可选文件
        try:
            category_list = self._load_json('category.json')
            attribute_list = self._load_json('attribute.json')
            visibility_list = self._load_json('visibility.json')
            instance_list = self._load_json('instance.json')
            sample_annotation_list = self._load_json('sample_annotation.json')
        except:
            category_list = []
            attribute_list = []
            visibility_list = []
            instance_list = []
            sample_annotation_list = []
        
        print("原始数据加载完成")
        
        # 过滤数据
        print("\n过滤数据...")
        filtered_data = self._filter_data(
            target_tokens,
            sample_list,
            scene_list,
            sample_data_list,
            ego_pose_list,
            calibrated_sensor_list,
            sensor_list,
            log_list,
            category_list,
            attribute_list,
            visibility_list,
            instance_list,
            sample_annotation_list
        )
        
        # 保存JSON文件
        print("\n保存元数据文件...")
        self._save_json(filtered_data['samples'], 
                       os.path.join(output_version_path, 'sample.json'))
        self._save_json(filtered_data['scenes'], 
                       os.path.join(output_version_path, 'scene.json'))
        self._save_json(filtered_data['sample_data'], 
                       os.path.join(output_version_path, 'sample_data.json'))
        self._save_json(filtered_data['ego_poses'], 
                       os.path.join(output_version_path, 'ego_pose.json'))
        self._save_json(filtered_data['calibrated_sensors'], 
                       os.path.join(output_version_path, 'calibrated_sensor.json'))
        self._save_json(filtered_data['sensors'], 
                       os.path.join(output_version_path, 'sensor.json'))
        self._save_json(filtered_data['logs'], 
                       os.path.join(output_version_path, 'log.json'))
        
        if filtered_data['categories']:
            self._save_json(filtered_data['categories'], 
                           os.path.join(output_version_path, 'category.json'))
        if filtered_data['attributes']:
            self._save_json(filtered_data['attributes'], 
                           os.path.join(output_version_path, 'attribute.json'))
        if filtered_data['visibilities']:
            self._save_json(filtered_data['visibilities'], 
                           os.path.join(output_version_path, 'visibility.json'))
        if filtered_data['instances']:
            self._save_json(filtered_data['instances'], 
                           os.path.join(output_version_path, 'instance.json'))
        if filtered_data['sample_annotations']:
            self._save_json(filtered_data['sample_annotations'], 
                           os.path.join(output_version_path, 'sample_annotation.json'))
        
        # 链接或复制数据文件
        print("\n处理数据文件...")
        self._link_data_files(
            output_dataroot,
            filtered_data['sample_data'],
            use_symlink
        )
        
        # 链接maps
        self._link_maps(output_dataroot, use_symlink)
        
        # 生成统计报告
        self._generate_version_report(
            output_dataroot,
            version_name,
            filtered_data,
            categories
        )
        
        print("\n" + "=" * 80)
        print("版本创建完成！")
        print("=" * 80)
        print(f"\n新版本路径: {output_dataroot}/{version_name}")
        
        return output_dataroot
    
    def _filter_data(self,
                     target_tokens: Set[str],
                     sample_list: List[Dict],
                     scene_list: List[Dict],
                     sample_data_list: List[Dict],
                     ego_pose_list: List[Dict],
                     calibrated_sensor_list: List[Dict],
                     sensor_list: List[Dict],
                     log_list: List[Dict],
                     category_list: List[Dict],
                     attribute_list: List[Dict],
                     visibility_list: List[Dict],
                     instance_list: List[Dict],
                     sample_annotation_list: List[Dict]) -> Dict:
        """
        过滤数据，只保留目标samples相关的所有数据
        """
        # 过滤samples
        filtered_samples = [s for s in sample_list if s['token'] in target_tokens]
        sample_tokens = {s['token'] for s in filtered_samples}
        
        print(f"  samples: {len(filtered_samples)}/{len(sample_list)}")
        
        # 获取相关的scene tokens
        scene_tokens = {s['scene_token'] for s in filtered_samples}
        filtered_scenes = [s for s in scene_list if s['token'] in scene_tokens]
        print(f"  scenes: {len(filtered_scenes)}/{len(scene_list)}")
        
        # 过滤sample_data（通过sample_token关联）
        filtered_sample_data = [
            sd for sd in sample_data_list 
            if sd.get('sample_token') in sample_tokens
        ]
        sample_data_tokens = {sd['token'] for sd in filtered_sample_data}
        print(f"  sample_data: {len(filtered_sample_data)}/{len(sample_data_list)}")
        
        # 获取相关的ego_pose tokens
        ego_pose_tokens = {sd['ego_pose_token'] for sd in filtered_sample_data 
                          if 'ego_pose_token' in sd}
        filtered_ego_poses = [ep for ep in ego_pose_list if ep['token'] in ego_pose_tokens]
        print(f"  ego_poses: {len(filtered_ego_poses)}/{len(ego_pose_list)}")
        
        # 获取相关的calibrated_sensor tokens
        calibrated_sensor_tokens = {
            sd['calibrated_sensor_token'] for sd in filtered_sample_data 
            if 'calibrated_sensor_token' in sd
        }
        filtered_calibrated_sensors = [
            cs for cs in calibrated_sensor_list 
            if cs['token'] in calibrated_sensor_tokens
        ]
        print(f"  calibrated_sensors: {len(filtered_calibrated_sensors)}/{len(calibrated_sensor_list)}")
        
        # 获取相关的sensor tokens
        sensor_tokens = {cs['sensor_token'] for cs in filtered_calibrated_sensors}
        filtered_sensors = [s for s in sensor_list if s['token'] in sensor_tokens]
        print(f"  sensors: {len(filtered_sensors)}/{len(sensor_list)}")
        
        # 获取相关的log tokens
        log_tokens = {scene['log_token'] for scene in filtered_scenes}
        filtered_logs = [log for log in log_list if log['token'] in log_tokens]
        print(f"  logs: {len(filtered_logs)}/{len(log_list)}")
        
        # 过滤annotations（如果有）
        filtered_annotations = []
        filtered_instances = []
        if sample_annotation_list:
            filtered_annotations = [
                ann for ann in sample_annotation_list 
                if ann.get('sample_token') in sample_tokens
            ]
            print(f"  annotations: {len(filtered_annotations)}/{len(sample_annotation_list)}")
            
            instance_tokens = {ann['instance_token'] for ann in filtered_annotations}
            filtered_instances = [
                inst for inst in instance_list 
                if inst['token'] in instance_tokens
            ]
            print(f"  instances: {len(filtered_instances)}/{len(instance_list)}")
        
        return {
            'samples': filtered_samples,
            'scenes': filtered_scenes,
            'sample_data': filtered_sample_data,
            'ego_poses': filtered_ego_poses,
            'calibrated_sensors': filtered_calibrated_sensors,
            'sensors': filtered_sensors,
            'logs': filtered_logs,
            'categories': category_list,  # 保留所有categories
            'attributes': attribute_list,  # 保留所有attributes
            'visibilities': visibility_list,  # 保留所有visibilities
            'instances': filtered_instances,
            'sample_annotations': filtered_annotations
        }
    
    def _link_data_files(self,
                        output_dataroot: str,
                        sample_data_list: List[Dict],
                        use_symlink: bool):
        """
        链接或复制数据文件
        """
        # 收集所有需要的文件路径
        file_paths = set()
        for sd in sample_data_list:
            if 'filename' in sd:
                file_paths.add(sd['filename'])
        
        print(f"  需要处理 {len(file_paths)} 个数据文件")
        
        # 创建必要的目录
        dirs_to_create = set()
        for filepath in file_paths:
            dir_path = os.path.dirname(filepath)
            dirs_to_create.add(dir_path)
        
        for dir_path in dirs_to_create:
            os.makedirs(os.path.join(output_dataroot, dir_path), exist_ok=True)
        
        # 链接或复制文件
        linked_count = 0
        failed_files = []
        
        for filepath in file_paths:
            src = os.path.join(self.original_dataroot, filepath)
            dst = os.path.join(output_dataroot, filepath)
            
            if os.path.exists(dst):
                linked_count += 1
                continue
            
            if not os.path.exists(src):
                failed_files.append(filepath)
                continue
            
            try:
                if use_symlink:
                    os.symlink(src, dst)
                else:
                    # 使用硬链接节省空间
                    os.link(src, dst)
                linked_count += 1
                
                if linked_count % 1000 == 0:
                    print(f"    已处理 {linked_count}/{len(file_paths)} 个文件")
            except Exception as e:
                failed_files.append(filepath)
        
        print(f"  ✓ 成功链接 {linked_count} 个文件")
        if failed_files:
            print(f"  ✗ 失败 {len(failed_files)} 个文件")
    
    def _link_maps(self, output_dataroot: str, use_symlink: bool):
        """链接maps目录"""
        src_maps = os.path.join(self.original_dataroot, 'maps')
        dst_maps = os.path.join(output_dataroot, 'maps')
        
        if os.path.exists(src_maps) and not os.path.exists(dst_maps):
            try:
                if use_symlink:
                    os.symlink(src_maps, dst_maps)
                else:
                    shutil.copytree(src_maps, dst_maps)
                print(f"  ✓ 已链接 maps 目录")
            except Exception as e:
                print(f"  ✗ 链接 maps 失败: {e}")
    
    def _generate_version_report(self,
                                 output_dataroot: str,
                                 version_name: str,
                                 filtered_data: Dict,
                                 categories: List[str]):
        """生成版本报告"""
        report_path = os.path.join(output_dataroot, f'{version_name}_report.txt')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"NuScenes版本报告: {version_name}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"包含的冗余度类别: {', '.join(categories)}\n\n")
            
            f.write("数据统计:\n")
            f.write(f"  Samples: {len(filtered_data['samples'])}\n")
            f.write(f"  Scenes: {len(filtered_data['scenes'])}\n")
            f.write(f"  Sample Data: {len(filtered_data['sample_data'])}\n")
            f.write(f"  Ego Poses: {len(filtered_data['ego_poses'])}\n")
            f.write(f"  Sensors: {len(filtered_data['sensors'])}\n")
            f.write(f"  Logs: {len(filtered_data['logs'])}\n")
            
            if filtered_data['sample_annotations']:
                f.write(f"  Annotations: {len(filtered_data['sample_annotations'])}\n")
                f.write(f"  Instances: {len(filtered_data['instances'])}\n")
        
        print(f"\n  已生成报告: {report_path}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='创建基于冗余度的完整NuScenes版本'
    )
    
    parser.add_argument(
        '--original-dataroot',
        type=str,
        default='/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes',
        help='原始NuScenes数据根目录'
    )
    
    parser.add_argument(
        '--original-version',
        type=str,
        default='v1.0-trainval',
        help='原始版本名称'
    )
    
    parser.add_argument(
        '--redundancy-split',
        type=str,
        default='./redundancy_split/redundancy_split.pkl',
        help='冗余度划分结果路径'
    )
    
    parser.add_argument(
        '--output-dataroot',
        type=str,
        default='./nuscenes_versions',
        help='输出数据根目录'
    )
    
    parser.add_argument(
        '--create-high',
        action='store_true',
        help='创建高冗余度版本'
    )
    
    parser.add_argument(
        '--create-low',
        action='store_true',
        help='创建低冗余度版本'
    )
    
    parser.add_argument(
        '--create-both',
        action='store_true',
        help='同时创建高冗余度和低冗余度版本'
    )
    
    parser.add_argument(
        '--use-symlink',
        action='store_true',
        default=True,
        help='使用符号链接（节省空间，默认启用）'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("NuScenes版本创建工具")
    print("=" * 80)
    
    # 创建版本生成器
    creator = NuScenesVersionCreator(
        original_dataroot=args.original_dataroot,
        original_version=args.original_version,
        redundancy_split_path=args.redundancy_split
    )
    
    # 决定创建哪些版本
    create_high = args.create_high or args.create_both
    create_low = args.create_low or args.create_both
    
    if not create_high and not create_low:
        print("\n请指定要创建的版本：")
        print("  --create-high  创建高冗余度版本")
        print("  --create-low   创建低冗余度版本")
        print("  --create-both  创建两个版本")
        return
    
    # 创建高冗余度版本
    if create_high:
        creator.create_version(
            output_dataroot=args.output_dataroot,
            version_name='v1.0-high-redundancy',
            categories=['high_redundancy'],
            use_symlink=args.use_symlink
        )
    
    # 创建低冗余度版本
    if create_low:
        creator.create_version(
            output_dataroot=args.output_dataroot,
            version_name='v1.0-low-redundancy',
            categories=['low_redundancy'],
            use_symlink=args.use_symlink
        )
    
    print("\n" + "=" * 80)
    print("全部完成！")
    print("=" * 80)
    print(f"\n新版本位置: {args.output_dataroot}/")
    print("\n使用方法：")
    print("  在MapTR中，将 data_root 设置为新版本的路径")
    print("  例如: data_root = './nuscenes_versions/v1.0-low-redundancy/'")


if __name__ == '__main__':
    main()

