#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NuScenes数据诊断工具
检查数据集结构是否正确
"""

import os
import json
import argparse


def diagnose_nuscenes_data(dataroot: str, version: str = 'v1.0-trainval'):
    """
    诊断NuScenes数据集
    
    Args:
        dataroot: 数据集根目录
        version: 版本
    """
    print("=" * 80)
    print("NuScenes数据集诊断")
    print("=" * 80)
    
    version_path = os.path.join(dataroot, version)
    print(f"\n数据路径: {version_path}")
    
    # 检查路径
    if not os.path.exists(version_path):
        print(f"❌ 错误: 路径不存在!")
        print(f"\n建议:")
        print(f"1. 检查dataroot是否正确: {dataroot}")
        print(f"2. 检查version是否正确: {version}")
        return False
    
    print(f"✓ 路径存在")
    
    # 检查必需文件
    required_files = ['sample.json', 'scene.json', 'sample_data.json', 'ego_pose.json']
    print(f"\n检查必需文件:")
    
    all_files_exist = True
    for filename in required_files:
        filepath = os.path.join(version_path, filename)
        exists = os.path.exists(filepath)
        status = "✓" if exists else "❌"
        
        if exists:
            size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            print(f"  {status} {filename} ({size:.2f} MB)")
        else:
            print(f"  {status} {filename} - 文件不存在!")
            all_files_exist = False
    
    if not all_files_exist:
        print(f"\n❌ 缺少必需文件!")
        return False
    
    # 加载和检查sample.json结构
    print(f"\n检查sample.json结构:")
    sample_path = os.path.join(version_path, 'sample.json')
    
    try:
        with open(sample_path, 'r') as f:
            samples = json.load(f)
        
        print(f"  ✓ 成功加载 {len(samples)} 个samples")
        
        if len(samples) == 0:
            print(f"  ❌ 警告: sample.json为空!")
            return False
        
        # 检查第一个sample的结构
        first_sample = samples[0]
        print(f"\n  第一个sample的结构:")
        print(f"    键 (keys): {list(first_sample.keys())}")
        
        # 检查必需字段
        required_fields = ['token', 'timestamp', 'scene_token', 'next', 'prev', 'data']
        missing_fields = []
        
        for field in required_fields:
            if field in first_sample:
                print(f"    ✓ {field}: {type(first_sample[field]).__name__}")
                if field == 'data':
                    # 详细检查data字段
                    print(f"      传感器: {list(first_sample['data'].keys())}")
            else:
                print(f"    ❌ 缺少字段: {field}")
                missing_fields.append(field)
        
        if missing_fields:
            print(f"\n  ❌ 错误: sample缺少必需字段: {missing_fields}")
            print(f"\n  这可能不是标准的NuScenes数据格式!")
            print(f"  请确保使用的是官方NuScenes数据集")
            return False
        
        # 检查LIDAR_TOP
        if 'LIDAR_TOP' not in first_sample['data']:
            print(f"\n  ❌ 警告: 第一个sample没有LIDAR_TOP传感器")
            print(f"     可用传感器: {list(first_sample['data'].keys())}")
        else:
            print(f"  ✓ LIDAR_TOP传感器存在")
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"  ❌ 读取错误: {e}")
        return False
    
    # 检查sample_data.json
    print(f"\n检查sample_data.json结构:")
    sample_data_path = os.path.join(version_path, 'sample_data.json')
    
    try:
        with open(sample_data_path, 'r') as f:
            sample_data_list = json.load(f)
        
        print(f"  ✓ 成功加载 {len(sample_data_list)} 个sample_data")
        
        if len(sample_data_list) > 0:
            first_sd = sample_data_list[0]
            print(f"  第一个sample_data的键: {list(first_sd.keys())}")
            
            if 'ego_pose_token' not in first_sd:
                print(f"  ❌ 警告: sample_data缺少ego_pose_token")
            else:
                print(f"  ✓ ego_pose_token存在")
    
    except Exception as e:
        print(f"  ❌ 读取错误: {e}")
        return False
    
    # 检查ego_pose.json
    print(f"\n检查ego_pose.json结构:")
    ego_pose_path = os.path.join(version_path, 'ego_pose.json')
    
    try:
        with open(ego_pose_path, 'r') as f:
            ego_poses = json.load(f)
        
        print(f"  ✓ 成功加载 {len(ego_poses)} 个ego_poses")
        
        if len(ego_poses) > 0:
            first_pose = ego_poses[0]
            print(f"  第一个ego_pose的键: {list(first_pose.keys())}")
            
            required_pose_fields = ['token', 'translation', 'rotation']
            for field in required_pose_fields:
                if field in first_pose:
                    print(f"  ✓ {field}: {first_pose[field]}")
                else:
                    print(f"  ❌ 缺少: {field}")
    
    except Exception as e:
        print(f"  ❌ 读取错误: {e}")
        return False
    
    # 总结
    print("\n" + "=" * 80)
    print("诊断完成")
    print("=" * 80)
    print("\n✓ 数据集结构正确，可以运行冗余度分析!")
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='诊断NuScenes数据集')
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
    
    args = parser.parse_args()
    
    success = diagnose_nuscenes_data(args.dataroot, args.version)
    
    if not success:
        print("\n" + "=" * 80)
        print("建议:")
        print("=" * 80)
        print("\n1. 确认NuScenes数据集已正确下载和解压")
        print("2. 确认数据集版本正确（v1.0-trainval, v1.0-test, v1.0-mini）")
        print("3. 确认dataroot路径指向正确的目录")
        print("\n数据集目录结构应该是:")
        print("  dataroot/")
        print("    └── v1.0-trainval/")
        print("        ├── sample.json")
        print("        ├── scene.json")
        print("        ├── sample_data.json")
        print("        ├── ego_pose.json")
        print("        └── ...")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())

