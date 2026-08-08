# 02 - 内核交叉编译环境

> 适用：Mainline Linux 6.18 内核 + `rk3568-gec-v11.dts` 板级适配。
> 目标：在 x86_64 Linux（WSL2 / 原生 Ubuntu）上交叉编译出 `Image` + `rk3568-gec-v11.dtb`，
> 再交回 Windows 端用 RKDevTool 打包 FIT / 烧写（本机不负责烧写）。

---

## 1. 交叉编译工具链

| 项 | 值 |
|----|----|
| 工具链 | Arm GNU Toolchain **15.2.Rel1**（Build arm-15.86） |
| 前缀 | `aarch64-none-linux-gnu-` |
| 获取 | [Arm 官方下载](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads) 或 `apt install gcc-aarch64-linux-gnu` |
| 验证 | `aarch64-none-linux-gnu-gcc --version` 应输出版本号 |

> 注：本项目早期用 `/opt/arm-toolchain/gcc-aarch64/bin/` 下的 15.2 工具链；apt 版（`gcc-aarch64-linux-gnu`，通常为 11/12/13）也能编过 6.18，版本差异不阻塞，只要能出 `aarch64` ELF 即可。

---

## 2. 环境变量（每次编译前 source）

```bash
export ARCH=arm64
export CROSS_COMPILE=aarch64-none-linux-gnu-
# 可选：指定输出目录，避免污染源码树
# export KBUILD_OUTPUT=../linux-rk3568-build
```

---

## 3. 内核源码来源

Mainline 6.18 源码在外部 fork（本仓库不存内核树）：

- 仓库：`https://github.com/Leon19960120/linux`
- 分支：`gecedu-rk3568-v6.18`（基于 upstream `v6.18`）
- 第一笔板级 commit：`arm64: dts: rockchip: add initial support for GecEdu RK3568 board`

本地克隆（WSL）：

```bash
cd ~
git clone --depth 1 -b gecedu-rk3568-v6.18 \
    https://github.com/Leon19960120/linux linux-rk3568
cd linux-rk3568
```

> ⚠️ 该仓库是从 torvalds/linux 浅克隆后首次 push 到空 fork 产生的，**首次 push 会传整个 v6.18 源码树（约 269 MiB）**，
> 这是浅克隆 + 空目标仓库的必然结果，不是你的代码改动大。后续改为 fork `rockchip-linux/kernel` 并切 BSP 分支后，
> 增量 push 只传 DTS diff（几 KB）。详见 `10_debug_notes.md` 续9。

---

## 4. 生成 .config（基线 + 必要开关）

主线 `defconfig` 不含 Rockchip 板级细节，需要补几处：

```bash
# 1) 基线：arm64 通用 defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- defconfig

# 2) 强制内核 cmdline（覆盖 U-Boot 传入的 ttyFIQ0，主线没有 fiq-debugger）
./scripts/config --enable  CONFIG_CMDLINE_FORCE
./scripts/config --set-str CONFIG_CMDLINE \
    "console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait"

# 3) 32-bit 用户态兼容（出厂 rootfs 是 AArch32 Buildroot，见 04_rootfs_compat.md）
./scripts/config --enable CONFIG_COMPAT

# 4) 打开主线 Mali GPU（Panfrost，学习用，无需厂商 DDK）
./scripts/config --enable CONFIG_DRM_PANFROST

# 5) 展开依赖
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- olddefconfig
```

实机验证过的完整配置见 `porting/mainline-6.18/configs/`：

- `rk3568-gec-v11-latest-working.config` —— **当前最新、实机验证**配置（bring-up 检查点）
- `history/rk3568-gec-v11-working.config` —— 初始 bring-up 检查点
- `history/rk3568-gec-v11-usb2-working.config` —— USB2 Host 打通检查点
- `history/rk3568-gec-v11-usb3-working.config` —— USB3 Host 打通检查点

可直接用最新配置起步：`cp porting/mainline-6.18/configs/rk3568-gec-v11-latest-working.config .config`

---

## 5. 编译内核与 DTB

```bash
# 完整编译（约 15~40 分钟，视机器）
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- Image dtbs

# 仅改了 DTS 后，只重编 dtb（快）
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- \
    rockchip/rk3568-gec-v11.dtb
```

产物：

- `arch/arm64/boot/Image`（约 39 MiB，**未压缩**；arm64 内核不自解压，需 gzip + U-Boot 解压，见 `01_boot_chain.md`）
- `arch/arm64/boot/Image.gz`（gzip 压缩版，FIT 用）
- `arch/arm64/boot/dts/rockchip/rk3568-gec-v11.dtb`

---

## 6. 一键构建脚本

`scripts/build-kernel.sh` 封装了「环境自检 → 拉源码 → 生成配置 → 编译」四步（阶段 0→1），
但**不烧写、不打包 FIT**（职责边界，避免越界）。注意该脚本目前写死 `torvalds/linux` 的 `v6.18`，
切到 BSP 6.6 时需改为 `rockchip-linux/kernel` 的 `develop-6.6`（见 `../rockchip-6.6/01_bsp_setup.md`）。

```bash
bash scripts/build-kernel.sh
```

---

## 7. 下一步

编译出的 `Image.gz` + `rk3568-gec-v11.dtb` 交给 `01_boot_chain.md` 的 FIT 打包流程 → RKDevTool 只烧 boot。

> 全部改动（DTS / config）都通过 `gecedu-rk3568-v6.18` 分支管理；本仓库 `GecEdu-RK3568`
> 只保存 `*.config` 检查点与 `fit-image.its` 模板，不保存内核源码。
