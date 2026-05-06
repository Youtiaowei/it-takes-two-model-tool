#!/bin/bash
# =============================================
# Linux → Windows 交叉编译脚本 (Docker)
# 使用 cdrx/pyinstaller-windows 镜像
# =============================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
OUTPUT_DIR="$PROJECT_DIR/dist"
DOCKER_IMAGE="cdrx/pyinstaller-windows:python3.11"

echo "============================================"
echo "  It Takes Two - Windows exe 交叉编译"
echo "============================================"
echo ""
echo "项目目录: $PROJECT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "[ERROR] 未找到 Docker，请先安装 Docker"
    echo "  安装: sudo apt install docker.io"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 拉取镜像
echo "[*] 准备 Docker 镜像..."
docker pull $DOCKER_IMAGE 2>/dev/null || true

# 创建临时构建脚本（在 Docker 内执行）
BUILD_SCRIPT=$(cat << 'DOCKER_SCRIPT'
set -e
echo "=== Docker 内构建 ==="

# 安装依赖
pip install pyinstaller --quiet

# 进入项目目录
cd /src

# 执行打包
echo "[*] 正在打包..."
pyinstaller \
    --onefile \
    --windowed \
    --name "ItTakesTwo_ModelSwapper" \
    --noconsole \
    --add-data "README.md;." \
    --hidden-import tkinter \
    --hidden-import tkinter.ttk \
    --hidden-import tkinter.filedialog \
    --hidden-import tkinter.messagebox \
    --clean \
    main.py

# 复制输出
cp dist/ItTakesTwo_ModelSwapper.exe /output/

echo "=== 构建完成 ==="
DOCKER_SCRIPT
)

echo "[*] 启动 Docker 容器进行交叉编译..."
echo "    这需要下载约 1GB 的基础镜像，请耐心等待..."
echo ""

# 运行 Docker
docker run --rm \
    -v "$PROJECT_DIR:/src" \
    -v "$OUTPUT_DIR:/output" \
    $DOCKER_IMAGE \
    bash -c "$BUILD_SCRIPT"

# 检查结果
if [ -f "$OUTPUT_DIR/ItTakesTwo_ModelSwapper.exe" ]; then
    EXE_SIZE=$(du -h "$OUTPUT_DIR/ItTakesTwo_ModelSwapper.exe" | cut -f1)
    echo ""
    echo "============================================"
    echo "  ✅ 交叉编译成功！"
    echo ""
    echo "  输出: $OUTPUT_DIR/ItTakesTwo_ModelSwapper.exe"
    echo "  大小: $EXE_SIZE"
    echo "============================================"
    echo ""
    echo "将此 exe 文件复制到 Windows 上，双击即可运行！"
else
    echo ""
    echo "  ❌ 编译失败，请检查错误信息"
    exit 1
fi
