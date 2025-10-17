#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试版本创建功能（小规模测试）
"""

from create_nuscenes_version import NuScenesVersionCreator
import os
import shutil

print("=" * 80)
print("测试版本创建功能")
print("=" * 80)

# 配置
original_dataroot = './data/nuscenes'
original_version = 'v1.0-trainval'
redundancy_split = './redundancy_split/redundancy_split.pkl'
output_dataroot = './test_nuscenes_versions'

# 清理旧的测试目录
if os.path.exists(output_dataroot):
    print(f"\n清理旧的测试目录: {output_dataroot}")
    shutil.rmtree(output_dataroot)

# 创建版本生成器
print("\n初始化版本创建器...")
creator = NuScenesVersionCreator(
    original_dataroot=original_dataroot,
    original_version=original_version,
    redundancy_split_path=redundancy_split
)

# 测试创建低冗余度版本
print("\n测试创建低冗余度版本...")
try:
    creator.create_version(
        output_dataroot=output_dataroot,
        version_name='v1.0-low-redundancy',
        categories=['low_redundancy'],
        use_symlink=True
    )
    print("\n✓ 低冗余度版本创建成功！")
except Exception as e:
    print(f"\n✗ 创建失败: {e}")
    import traceback
    traceback.print_exc()

# 验证生成的文件
print("\n验证生成的文件...")
version_path = os.path.join(output_dataroot, 'v1.0-low-redundancy')
required_files = [
    'sample.json',
    'scene.json',
    'sample_data.json',
    'ego_pose.json',
    'calibrated_sensor.json',
    'sensor.json',
    'log.json'
]

all_exist = True
for filename in required_files:
    filepath = os.path.join(version_path, filename)
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"  {status} {filename}")
    if not exists:
        all_exist = False

if all_exist:
    print("\n✓✓✓ 所有测试通过！")
    print(f"\n测试版本位置: {output_dataroot}")
    print("\n可以使用完整功能了:")
    print("  ./create_versions.sh")
else:
    print("\n✗ 部分文件缺失")

print("\n提示: 测试目录可以删除")
print(f"  rm -rf {output_dataroot}")

