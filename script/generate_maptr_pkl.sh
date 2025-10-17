#!/bin/bash

# 生成MapTR pkl索引文件 - 一键脚本

echo "=========================================="
echo "生成MapTR pkl索引文件"
echo "=========================================="
echo ""

# 默认配置
REDUNDANCY_SPLIT="./redundancy_split/redundancy_split.pkl"
ORIGINAL_TRAIN="./data/nuscenes/nuscenes_infos_temporal_train.pkl"
ORIGINAL_VAL="./data/nuscenes/nuscenes_infos_temporal_val.pkl"
OUTPUT_DIR="./maptr_low_redundancy"

# 检查冗余度划分文件
if [ ! -f "$REDUNDANCY_SPLIT" ]; then
    echo "错误: 找不到冗余度划分文件: $REDUNDANCY_SPLIT"
    echo ""
    echo "请先运行冗余度分析："
    echo "  bash script/analyze_redundancy.sh"
    exit 1
fi

# 检查原始MapTR pkl文件
if [ ! -f "$ORIGINAL_TRAIN" ]; then
    echo "错误: 找不到原始训练集文件: $ORIGINAL_TRAIN"
    echo ""
    echo "请先准备MapTR数据："
    echo "  cd /path/to/MapTR"
    echo "  python tools/create_data.py nuscenes --root-path ./data/nuscenes --out-dir ./data/nuscenes --extra-tag nuscenes --version v1.0 --canbus ./data"
    echo ""
    echo "或者修改脚本中的 ORIGINAL_TRAIN 和 ORIGINAL_VAL 路径"
    exit 1
fi

if [ ! -f "$ORIGINAL_VAL" ]; then
    echo "错误: 找不到原始验证集文件: $ORIGINAL_VAL"
    exit 1
fi

# 选择生成模式
echo "请选择生成模式："
echo "  1) 仅低冗余度 (推荐，最快训练速度)"
echo "  2) 自定义比例 (70%低冗余 + 30%中冗余)"
echo "  3) 平衡各类冗余度"
echo ""
read -p "请输入选项 [1-3]: " MODE_CHOICE

case $MODE_CHOICE in
    1)
        MODE="low_only"
        OUTPUT_DIR="./maptr_low_redundancy"
        echo "选择: 仅低冗余度数据"
        ;;
    2)
        MODE="custom"
        OUTPUT_DIR="./maptr_custom"
        echo "选择: 自定义比例 (70%低 + 30%中)"
        LOW_RATIO=0.7
        MEDIUM_RATIO=0.3
        HIGH_RATIO=0.0
        ;;
    3)
        MODE="balanced"
        OUTPUT_DIR="./maptr_balanced"
        echo "选择: 平衡各类冗余度"
        ;;
    *)
        echo "无效选项，使用默认：仅低冗余度"
        MODE="low_only"
        OUTPUT_DIR="./maptr_low_redundancy"
        ;;
esac

echo ""
echo "配置："
echo "  冗余度划分: $REDUNDANCY_SPLIT"
echo "  原始训练集: $ORIGINAL_TRAIN"
echo "  原始验证集: $ORIGINAL_VAL"
echo "  输出目录: $OUTPUT_DIR"
echo "  模式: $MODE"
echo ""

read -p "按 Enter 继续，Ctrl+C 取消..."

# 运行生成器
echo ""
echo "开始生成MapTR pkl索引文件..."
echo "----------------------------------------"

if [ "$MODE" == "custom" ]; then
    python tools/generate_maptr_pkl.py \
        --redundancy-split "$REDUNDANCY_SPLIT" \
        --original-train "$ORIGINAL_TRAIN" \
        --original-val "$ORIGINAL_VAL" \
        --output-dir "$OUTPUT_DIR" \
        --mode custom \
        --low-ratio $LOW_RATIO \
        --medium-ratio $MEDIUM_RATIO \
        --high-ratio $HIGH_RATIO
else
    python tools/generate_maptr_pkl.py \
        --redundancy-split "$REDUNDANCY_SPLIT" \
        --original-train "$ORIGINAL_TRAIN" \
        --original-val "$ORIGINAL_VAL" \
        --output-dir "$OUTPUT_DIR" \
        --mode "$MODE"
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "错误: 生成失败"
    exit 1
fi

# 完成
echo ""
echo "=========================================="
echo "生成完成！"
echo "=========================================="
echo ""
echo "生成的文件位置:"
echo "  $OUTPUT_DIR/nuscenes_infos_temporal_train.pkl"
echo "  $OUTPUT_DIR/nuscenes_infos_temporal_val.pkl"
echo "  $OUTPUT_DIR/maptr_split_report.txt"
echo ""

# 显示报告
if [ -f "$OUTPUT_DIR/maptr_split_report.txt" ]; then
    echo "数据统计："
    echo "----------------------------------------"
    cat "$OUTPUT_DIR/maptr_split_report.txt"
    echo "----------------------------------------"
    echo ""
fi

echo "在MapTR中使用："
echo ""
echo "方法1 - 修改配置文件："
echo "  # 在MapTR配置文件中设置："
echo "  data = dict("
echo "      train=dict("
echo "          data_root='data/nuscenes/',  # 原始数据路径"
echo "          ann_file='$OUTPUT_DIR/nuscenes_infos_temporal_train.pkl',  # 新索引"
echo "      ),"
echo "      val=dict("
echo "          data_root='data/nuscenes/',"
echo "          ann_file='$OUTPUT_DIR/nuscenes_infos_temporal_val.pkl',"
echo "      ),"
echo "  )"
echo ""
echo "方法2 - 使用软链接："
echo "  cd /path/to/MapTR/data/nuscenes"
echo "  mv nuscenes_infos_temporal_train.pkl nuscenes_infos_temporal_train.pkl.bak"
echo "  mv nuscenes_infos_temporal_val.pkl nuscenes_infos_temporal_val.pkl.bak"
echo "  ln -s $(pwd)/$OUTPUT_DIR/nuscenes_infos_temporal_train.pkl ."
echo "  ln -s $(pwd)/$OUTPUT_DIR/nuscenes_infos_temporal_val.pkl ."
echo ""

