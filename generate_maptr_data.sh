#!/bin/bash

# 一键生成MapTR低冗余度数据脚本

echo "=========================================="
echo "生成MapTR低冗余度数据"
echo "=========================================="
echo ""

# 默认路径配置
REDUNDANCY_SPLIT="/data2/file_swap/sh_space/nuscenes_NewSplit/redundancy_split/redundancy_split.pkl"
ORIGINAL_TRAIN="/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes/nuscenes_infos_temporal_train.pkl"
ORIGINAL_VAL="/data2/file_swap/sh_space/nuscenes_NewSplit/data/nuscenes/nuscenes_infos_temporal_val.pkl"
OUTPUT_DIR="/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy"

# 检查冗余度划分文件是否存在
if [ ! -f "$REDUNDANCY_SPLIT" ]; then
    echo "错误: 找不到冗余度划分文件: $REDUNDANCY_SPLIT"
    echo ""
    echo "请先运行冗余度分析："
    echo "  python split_by_redundancy.py"
    exit 1
fi

# 检查原始MapTR数据文件
if [ ! -f "$ORIGINAL_TRAIN" ]; then
    echo "错误: 找不到原始训练集文件: $ORIGINAL_TRAIN"
    echo ""
    echo "请先准备MapTR数据："
    echo "  cd /path/to/MapTR"
    echo "  python tools/create_data.py nuscenes --root-path ./data/nuscenes --out-dir ./data/nuscenes --extra-tag nuscenes --version v1.0 --canbus ./data"
    exit 1
fi

if [ ! -f "$ORIGINAL_VAL" ]; then
    echo "错误: 找不到原始验证集文件: $ORIGINAL_VAL"
    exit 1
fi

# 选择模式
echo "请选择生成模式："
echo "  1) 仅低冗余度数据（推荐，最快训练速度）"
echo "  2) 自定义比例（70%低冗余 + 30%中冗余）"
echo "  3) 平衡各类冗余度"
echo ""
read -p "请输入选项 [1-3]: " MODE_CHOICE

case $MODE_CHOICE in
    1)
        MODE="low_only"
        OUTPUT_DIR="/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy"
        echo "选择: 仅低冗余度数据"
        ;;
    2)
        MODE="custom"
        OUTPUT_DIR="/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_custom"
        echo "选择: 自定义比例"
        ;;
    3)
        MODE="balanced"
        OUTPUT_DIR="/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_balanced"
        echo "选择: 平衡各类冗余度"
        ;;
    *)
        echo "无效选项，使用默认：仅低冗余度数据"
        MODE="low_only"
        OUTPUT_DIR="/data2/file_swap/sh_space/nuscenes_NewSplit/maptr_low_redundancy"
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

read -p "按Enter继续，Ctrl+C取消..."

# 运行适配器
echo ""
echo "开始生成MapTR数据..."
echo "----------------------------------------"

if [ "$MODE" == "custom" ]; then
    python maptr_adapter.py \
        --redundancy-split "$REDUNDANCY_SPLIT" \
        --original-train "$ORIGINAL_TRAIN" \
        --original-val "$ORIGINAL_VAL" \
        --output-dir "$OUTPUT_DIR" \
        --mode custom \
        --low-ratio 0.7 \
        --medium-ratio 0.3 \
        --high-ratio 0.0
else
    python maptr_adapter.py \
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
echo ""
echo "下一步："
echo ""
echo "方法1 - 在MapTR中使用软链接："
echo "  cd /path/to/MapTR/data/nuscenes"
echo "  mv nuscenes_infos_temporal_train.pkl nuscenes_infos_temporal_train.pkl.bak"
echo "  mv nuscenes_infos_temporal_val.pkl nuscenes_infos_temporal_val.pkl.bak"
echo "  ln -s $OUTPUT_DIR/nuscenes_infos_temporal_train.pkl ."
echo "  ln -s $OUTPUT_DIR/nuscenes_infos_temporal_val.pkl ."
echo ""
echo "方法2 - 修改MapTR配置文件："
echo "  在配置文件中设置："
echo "  data_root = '$OUTPUT_DIR/'"
echo ""
echo "然后运行MapTR训练命令"
echo ""

