#!/bin/bash

# 创建完整的NuScenes版本（高冗余度和低冗余度）

echo "=========================================="
echo "创建NuScenes完整版本"
echo "=========================================="
echo ""

# 配置
ORIGINAL_DATAROOT="/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes"
REDUNDANCY_SPLIT="./redundancy_split/redundancy_split.pkl"
OUTPUT_DATAROOT="./nuscenes_versions"

# 检查冗余度划分文件
if [ ! -f "$REDUNDANCY_SPLIT" ]; then
    echo "错误: 找不到冗余度划分文件: $REDUNDANCY_SPLIT"
    echo "请先运行: python split_by_redundancy.py"
    exit 1
fi

# 选择模式
echo "请选择要创建的版本："
echo "  1) 高冗余度版本 (v1.0-high-redundancy)"
echo "  2) 低冗余度版本 (v1.0-low-redundancy)"
echo "  3) 同时创建两个版本"
echo ""
read -p "请输入选项 [1-3]: " CHOICE

case $CHOICE in
    1)
        MODE="--create-high"
        echo "将创建: 高冗余度版本"
        ;;
    2)
        MODE="--create-low"
        echo "将创建: 低冗余度版本"
        ;;
    3)
        MODE="--create-both"
        echo "将创建: 高冗余度和低冗余度版本"
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "配置:"
echo "  原始数据: $ORIGINAL_DATAROOT"
echo "  输出目录: $OUTPUT_DATAROOT"
echo "  使用方式: 符号链接（节省空间）"
echo ""

read -p "按Enter继续，Ctrl+C取消..."

# 运行创建脚本
echo ""
echo "开始创建版本..."
echo "----------------------------------------"

python create_nuscenes_version.py \
    --original-dataroot "$ORIGINAL_DATAROOT" \
    --original-version v1.0-trainval \
    --redundancy-split "$REDUNDANCY_SPLIT" \
    --output-dataroot "$OUTPUT_DATAROOT" \
    $MODE \
    --use-symlink

if [ $? -ne 0 ]; then
    echo ""
    echo "错误: 创建失败"
    exit 1
fi

# 显示结果
echo ""
echo "=========================================="
echo "创建完成！"
echo "=========================================="
echo ""
echo "新版本位置:"

if [ "$CHOICE" = "1" ] || [ "$CHOICE" = "3" ]; then
    echo "  高冗余度: $OUTPUT_DATAROOT/v1.0-high-redundancy/"
fi

if [ "$CHOICE" = "2" ] || [ "$CHOICE" = "3" ]; then
    echo "  低冗余度: $OUTPUT_DATAROOT/v1.0-low-redundancy/"
fi

echo ""
echo "目录结构:"
echo "  nuscenes_versions/"
echo "    ├── v1.0-high-redundancy/ (或 v1.0-low-redundancy/)"
echo "    │   ├── sample.json"
echo "    │   ├── scene.json"
echo "    │   ├── sample_data.json"
echo "    │   ├── ego_pose.json"
echo "    │   └── ..."
echo "    ├── samples/ (符号链接)"
echo "    ├── sweeps/ (符号链接)"
echo "    └── maps/ (符号链接)"
echo ""
echo "使用方法:"
echo "  在MapTR配置中设置："
echo "  data_root = './nuscenes_versions/v1.0-low-redundancy/'"
echo ""

