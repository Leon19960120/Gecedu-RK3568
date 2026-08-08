#!/usr/bin/env bash
#
# scripts/build-kernel.sh
# ============================================================
# 用途：在已就绪的 Linux 6.18 内核树（GEC RK3568 V1.1 / rk3568-gec-v11）
#       里，交叉编译并打包可重复的 boot.img（FIT 镜像）。
#
# 它主要干 3 件事：
#   1) 环境自检   —— 确认 Linux 环境、交叉工具链、mkimage 就绪
#   2) 编译产物   —— Image.gz + rockchip/rk3568-gec-v11.dtb
#   3) 打包 FIT   —— 用 fit-image.its + mkimage 生成 32 MiB boot.img
#
# 它【不】干的事（职责边界，避免越界）：
#   × 不自动 clone / 拉取内核源码（请把内核树先放到 KERNEL_DIR）
#   × 不下载 / 安装工具链（自备 aarch64-none-linux-gnu- 与 U-Boot mkimage）
#   × 不修改 / 不自动生成 .config（config 与 bootargs 由使用者预先配好；
#     内核树缺 .config 时直接报错退出，绝不自动复制或改写任何 config 选项）
#   × 不刷机（烧写用 Windows 端 RKDevTool 手动做）
#
# 期望的内核树：
#   Leon19960120/linux 的 gecedu-rk3568-v6.18 分支（含 rk3568-gec-v11.dts）
#
# 用法：
#   KERNEL_DIR=~/linux-rk3568 bash scripts/build-kernel.sh
# 产物（均在 KERNEL_DIR 下）：
#   arch/arm64/boot/Image.gz
#   arch/arm64/boot/dts/rockchip/rk3568-gec-v11.dtb
#   boot.img   (32 MiB FIT 镜像)
# ============================================================
set -euo pipefail

# ---------- 可配置变量（按需修改） ----------
# 内核树目录（需已 clone 并配好 .config；本脚本不负责拉取）
KERNEL_DIR="${KERNEL_DIR:-${HOME}/linux-rk3568}"
# 仅引用项目内的 fit-image.its；不引用任何 kernel config（Commit 4 原则：不改 config）
SOURCE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# FIT 源描述文件（只读复用，不改其中 bootargs）
FIT_ITS_SOURCE="${SOURCE_ROOT}/porting/mainline-6.18/boot/fit-image.its"

ARCH="arm64"
CROSS_COMPILE="aarch64-none-linux-gnu-"
DTB="rockchip/rk3568-gec-v11.dtb"   # GEC 板专用，非 evb1-v10
FIT_ITS="${KERNEL_DIR}/fit-image.its"
BOOT_IMG="${KERNEL_DIR}/boot.img"
BOOT_IMG_MAX_BYTES=33554432          # 32 MiB，适配出厂 boot 分区
mkimage_flags=(-E -p 0x800)          # 外部数据 + 0x800 页对齐

# ---------- 0. 环境自检 ----------
echo "==> [0/3] 环境自检"
if [ "$(uname)" != "Linux" ]; then
  echo "错误：本脚本必须在 Linux（WSL2 / 原生 Ubuntu）下运行，不能在 Windows 直接跑。" >&2
  exit 1
fi
for bin in make git bc flex bison; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "缺少命令：$bin，请先安装构建依赖（如 apt install build-essential libncurses-dev flex bison）。" >&2
    exit 1
  fi
done
if ! command -v "${CROSS_COMPILE}gcc" >/dev/null 2>&1; then
  echo "缺少交叉编译器 ${CROSS_COMPILE}gcc，请先安装 ARM GNU 工具链（aarch64-none-linux-gnu-）。" >&2
  exit 1
fi
if ! command -v mkimage >/dev/null 2>&1; then
  echo "缺少 mkimage（U-Boot 工具），请先安装 u-boot-tools 或将其加入 PATH。" >&2
  exit 1
fi
echo "    工具链 OK：$(${CROSS_COMPILE}gcc --version | head -1)"

# ---------- 1. 校验内核树与 .config / fit-image.its 就绪 ----------
echo "==> [1/3] 校验内核树与 .config"
if [ ! -d "$KERNEL_DIR/.git" ]; then
  echo "错误：未找到内核树 $KERNEL_DIR（本脚本不负责 clone）。" >&2
  echo "      请先手动拉取 Leon19960120/linux 的 gecedu-rk3568-v6.18 分支到该目录并配好 .config。" >&2
  exit 1
fi
cd "$KERNEL_DIR"
if [ ! -f ".config" ]; then
  echo "错误：内核树 $KERNEL_DIR 下无 .config；本脚本不自动复制或改写 kernel config。" >&2
  echo "      请先在内核树内准备好 .config（Commit 4 原则：不自动改 kernel config）。" >&2
  exit 1
fi
# fit-image.its 内 incbin 路径相对运行 mkimage 的 CWD（=KERNEL_DIR）解析，
# 故将其放到 KERNEL_DIR 下，避免 incbin 找不到 Image.gz / dtb。
if [ ! -f "$FIT_ITS" ]; then
  echo "    内核树下无 fit-image.its，复制项目内的：$FIT_ITS_SOURCE"
  cp "$FIT_ITS_SOURCE" "$FIT_ITS"
fi

# ---------- 2. 编译 ----------
echo "==> [2/3] 编译 Image.gz + ${DTB}（这步最久，约 15~40 分钟）"
jobs="$(nproc)"
if [ "$jobs" -lt 4 ]; then jobs=4; fi
make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" -j"$jobs" Image.gz dtbs

# ---------- 3. 打包 FIT boot.img ----------
echo "==> [3/3] 打包 FIT boot.img"
# mkimage 在 KERNEL_DIR 下运行，fit-image.its 内 incbin 相对此处解析 Image.gz / dtb
rm -f "$BOOT_IMG"
mkimage "${mkimage_flags[@]}" -f "$FIT_ITS" "$BOOT_IMG"
fit_size="$(stat -c %s "$BOOT_IMG")"
if [ "$fit_size" -gt "$BOOT_IMG_MAX_BYTES" ]; then
  echo "错误：FIT 镜像 ${fit_size} 字节已超过 32 MiB 上限，停止打包（请检查内核是否过大）。" >&2
  exit 1
fi
# 适配出厂 32 MiB boot 分区：补零到固定大小（FIT 内容通常远小于 32 MiB，安全）
truncate -s "$BOOT_IMG_MAX_BYTES" "$BOOT_IMG"
mkimage -l "$BOOT_IMG"
echo "boot.img: $BOOT_IMG"
echo
echo "下一步：Windows 端用 RKDevTool 把 boot.img 烧到 boot 分区（只烧 boot，不动其他分区）。"
