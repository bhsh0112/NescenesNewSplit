#!/bin/bash

# NuScenes数据冗余度分析与可视化 - 一键脚本

echo "=========================================="
echo "NuScenes数据冗余度分析与可视化"
echo "=========================================="
echo ""

# 默认配置
DATAROOT="/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes"
VERSION="v1.0-trainval"
OUTPUT_DIR="./redundancy_split"
LOW_VELOCITY=1.0
HIGH_VELOCITY=5.0

# 检查数据集路径
if [ ! -d "$DATAROOT" ]; then
    echo "错误: 找不到数据集目录: $DATAROOT"
    echo ""
    echo "请修改脚本中的 DATAROOT 变量，或创建符号链接："
    echo "  ln -s /path/to/your/nuscenes ./data/nuscenes"
    exit 1
fi

# 检查版本目录
VERSION_PATH="$DATAROOT/$VERSION"
if [ ! -d "$VERSION_PATH" ]; then
    echo "错误: 找不到版本目录: $VERSION_PATH"
    echo ""
    echo "可用的版本："
    ls -d "$DATAROOT"/v1.0-* 2>/dev/null | xargs -n 1 basename
    exit 1
fi

echo "配置信息："
echo "  数据路径: $DATAROOT"
echo "  版本: $VERSION"
echo "  输出目录: $OUTPUT_DIR"
echo "  低速阈值: $LOW_VELOCITY m/s"
echo "  高速阈值: $HIGH_VELOCITY m/s"
echo ""

# 询问是否继续
read -p "按 Enter 继续，Ctrl+C 取消..."
echo ""

# 步骤1: 冗余度分析
echo "=========================================="
echo "步骤 1/2: 分析数据冗余度"
echo "=========================================="
echo ""

python tools/split_by_redundancy.py \
    --dataroot "$DATAROOT" \
    --version "$VERSION" \
    --output-dir "$OUTPUT_DIR" \
    --low-velocity "$LOW_VELOCITY" \
    --high-velocity "$HIGH_VELOCITY"

if [ $? -ne 0 ]; then
    echo ""
    echo "错误: 冗余度分析失败"
    exit 1
fi

# 检查分析结果
if [ ! -f "$OUTPUT_DIR/redundancy_split.pkl" ]; then
    echo ""
    echo "错误: 未生成分析结果文件"
    exit 1
fi

echo ""
echo "✓ 冗余度分析完成"
echo ""

# 步骤2: 可视化
echo "=========================================="
echo "步骤 2/2: 生成可视化图表"
echo "=========================================="
echo ""

python tools/visualize_redundancy.py \
    --result-path "$OUTPUT_DIR/redundancy_split.pkl" \
    --output-dir "$OUTPUT_DIR"

if [ $? -ne 0 ]; then
    echo ""
    echo "警告: 可视化生成失败（分析结果已保存）"
else
    echo ""
    echo "✓ 可视化完成"
fi

# 完成
echo ""
echo "=========================================="
echo "全部完成！"
echo "=========================================="
echo ""

# 显示结果
echo "生成的文件："
echo ""
echo "分析结果："
echo "  $OUTPUT_DIR/redundancy_split.pkl"
echo "  $OUTPUT_DIR/redundancy_split.json"
echo "  $OUTPUT_DIR/redundancy_report.txt"
echo ""
echo "样本列表："
echo "  $OUTPUT_DIR/high_redundancy_sample_tokens.txt"
echo "  $OUTPUT_DIR/medium_redundancy_sample_tokens.txt"
echo "  $OUTPUT_DIR/low_redundancy_sample_tokens.txt"
echo ""

if [ -f "$OUTPUT_DIR/redundancy_distribution.png" ]; then
    echo "可视化图表："
    echo "  $OUTPUT_DIR/redundancy_distribution.png"
    echo "  $OUTPUT_DIR/velocity_histogram.png"
    echo "  $OUTPUT_DIR/redundancy_scatter.png"
    echo "  $OUTPUT_DIR/redundancy_pie_charts.png"
    echo ""
fi

# 显示统计摘要
if [ -f "$OUTPUT_DIR/redundancy_report.txt" ]; then
    echo "数据统计摘要："
    echo "----------------------------------------"
    cat "$OUTPUT_DIR/redundancy_report.txt" | head -20
    echo "----------------------------------------"
    echo ""
    echo "查看完整报告："
    echo "  cat $OUTPUT_DIR/redundancy_report.txt"
    echo ""
fi

echo "下一步："
echo "  1. 查看可视化图表了解数据分布"
echo "  2. 运行 'bash script/create_versions.sh' 创建新版本"
echo "  3. 或运行 'python tools/maptr_adapter.py' 生成MapTR索引"
echo ""
