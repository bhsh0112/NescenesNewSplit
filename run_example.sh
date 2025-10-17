#!/bin/bash

# NuScenes数据集冗余度划分 - 快速开始脚本

echo "=========================================="
echo "NuScenes数据集冗余度划分"
echo "=========================================="
echo ""

# 设置路径
DATAROOT="/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes"
OUTPUT_DIR="/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split"

# 检查数据集是否存在
if [ ! -d "$DATAROOT" ]; then
    echo "错误: 找不到数据集目录: $DATAROOT"
    exit 1
fi

if [ ! -d "$DATAROOT/v1.0-trainval" ]; then
    echo "错误: 找不到v1.0-trainval目录"
    exit 1
fi

echo "数据集路径: $DATAROOT"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 步骤1: 数据划分
echo "步骤1: 开始数据划分..."
echo "----------------------------------------"
python split_by_redundancy.py \
    --dataroot "$DATAROOT" \
    --version v1.0-trainval \
    --output-dir "$OUTPUT_DIR" \
    --low-velocity 1.0 \
    --high-velocity 5.0 \
    --high-redundancy-threshold 0.6 \
    --low-redundancy-threshold 0.3

if [ $? -ne 0 ]; then
    echo "错误: 数据划分失败"
    exit 1
fi

echo ""
echo "步骤1完成！"
echo ""

# 步骤2: 可视化
echo "步骤2: 生成可视化图表..."
echo "----------------------------------------"
python visualize_redundancy.py \
    --result-path "$OUTPUT_DIR/redundancy_split.pkl" \
    --output-dir "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo "错误: 可视化失败"
    exit 1
fi

echo ""
echo "步骤2完成！"
echo ""

# 完成
echo "=========================================="
echo "全部完成！"
echo "=========================================="
echo ""
echo "结果已保存到: $OUTPUT_DIR"
echo ""
echo "生成的文件:"
echo "  - redundancy_split.pkl          (划分结果-pickle格式)"
echo "  - redundancy_split.json         (划分结果-JSON格式)"
echo "  - redundancy_report.txt         (统计报告)"
echo "  - *_sample_tokens.txt           (各类别样本token)"
echo "  - *.png                         (可视化图表)"
echo ""
echo "查看统计报告:"
echo "  cat $OUTPUT_DIR/redundancy_report.txt"
echo ""

