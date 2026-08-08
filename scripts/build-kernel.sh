#!/usr/bin/env bash
#
# scripts/build-kernel.sh
# ============================================================
# 用途：在 WSL2 / Ubuntu（Linux 环境）里，一键拉取并交叉编译
#       适用于 RK3568 的主线内核（阶段 0 → 阶段 1）。
#
# 它主要干 4 件事：
#   1) 环境自检   —— 确认在 Linux 下、交叉工具链/依赖齐全
#   2) 拉取源码   —— 幂等 clone 主线 6.18 LTS（已存在则跳过）
#   3) 生成配置   —— rockchip_defconfig + 改 console
#   4) 编译产物   —— Image + rk3568-evb1-v10.dtb
#
# 它【不】干的事（职责边界，避免越界）：
#   × 不烧写（烧写用 Windows 端 RKDevTool 手动做）
#   × 不打包 boot.img（阶段 1 后期单独处理，需要 RK 的 FIT 工具）
#   × 不改 U-Boot、不碰屏驱动（屏是阶段 3）
#
# 用法：
#   bash scripts/build-kernel.sh
# 产物：
#   ~/linux-rk3568/arch/arm64/boot/Image
#   ~/linux-rk3568/arch/arm64/boot/dts/rockchip/rk3568-evb1-v10.dtb
# ============================================================
set -euo pipefail

# ---------- 可配置变量（按需修改） ----------
KERNEL_REPO="https://github.com/torvalds/linux.git"
KERNEL_BRANCH="v6.18"
KERNEL_DIR="${HOME}/linux-rk3568"
ARCH="arm64"
CROSS_COMPILE="aarch64-none-linux-gnu-"
DEFCONFIG="defconfig"

# 调试串口：厂商 4.19 用 ttyFIQ0（fiq-debugger），主线无 fiq-debugger，
# RK3568 的调试串口是 serial2 = ttyS2。保留厂商 U-Boot 时，最省事的做法
# 是让内核强制使用自己的 cmdline（覆盖 U-Boot 传入的 ttyFIQ0）。
FORCE_KERNEL_CMDLINE="true"
KERNEL_CMDLINE="console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait"

# ---------- 0. 环境自检 ----------
echo "==> [0/4] 环境自检"
if [ "$(uname)" != "Linux" ]; then
  echo "错误：本脚本必须在 Linux（WSL2 / 原生 Ubuntu）下运行，不能在 Windows cmd/PowerShell 直接跑。"
  exit 1
fi
for bin in make gcc git bc flex bison; do
  command -v "$bin" >/dev/null 2>&1 || { echo "缺少命令：$bin，请先 apt install 构建依赖"; exit 1; }
done
if ! command -v "${CROSS_COMPILE}gcc" >/dev/null 2>&1; then
  echo "缺少交叉编译器 ${CROSS_COMPILE}gcc，请先："
  echo "  sudo apt install gcc-aarch64-linux-gnu"
  exit 1
fi
echo "    工具链 OK：$(${CROSS_COMPILE}gcc --version | head -1)"

# ---------- 1. 拉取源码（幂等） ----------
echo "==> [1/4] 获取内核源码"
if [ -d "$KERNEL_DIR/.git" ]; then
  echo "    源码已存在于 $KERNEL_DIR，跳过 clone（如需更新请手动：git -C $KERNEL_DIR pull）"
else
  echo "    clone $KERNEL_BRANCH 到 $KERNEL_DIR ..."
  git clone --depth 1 -b "$KERNEL_BRANCH" "$KERNEL_REPO" "$KERNEL_DIR"
fi

# ---------- 2. 生成配置 ----------
echo "==> [2/4] 生成 .config"
cd "$KERNEL_DIR"
make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" "$DEFCONFIG"
if [ "$FORCE_KERNEL_CMDLINE" = "true" ]; then
  ./scripts/config --enable  CONFIG_CMDLINE_FORCE
  ./scripts/config --set-str CONFIG_CMDLINE "$KERNEL_CMDLINE"
  echo "    已强制内核 cmdline：$KERNEL_CMDLINE"
else
  ./scripts/config --disable CONFIG_CMDLINE_FORCE
  echo "    未强制内核 cmdline，需在 U-Boot 里把 bootargs 的 console 改为 ttyS2,1500000"
fi
# 打开 Panfrost（主线 Mali GPU 驱动，学习用；不依赖厂商 DDK）
./scripts/config --enable CONFIG_DRM_PANFROST
# 重新展开依赖
make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" olddefconfig

# ---------- 3. 编译 ----------
echo "==> [3/4] 编译 Image + dtbs（这步最久，约 15~40 分钟）"
JOBS=$(nproc)
if [ "$JOBS" -lt 4 ]; then JOBS=4; fi
make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" -j"$JOBS" Image dtbs

# ---------- 4. 产物 ----------
echo "==> [4/4] 完成"
echo "Image: $KERNEL_DIR/arch/arm64/boot/Image"
echo "DTB:   $KERNEL_DIR/arch/arm64/boot/dts/rockchip/rk3568-evb1-v10.dtb"
echo
echo "下一步：在 Windows 端用 RKDevTool 把上面两个文件打包进 boot.img 烧到 boot 分区。"
echo "（打包步骤见 docs/porting/mainline-7.x-porting.md 阶段 1）"
