# GecEdu RK3568 — Linux Bring-up

针对自定义 **GecEdu RK3568 开发板** 进行的 Linux 系统移植与验证项目，覆盖：

- Linux bring-up（主线内核板级启动）
- Device Tree 适配
- 外设驱动验证（Ethernet / USB / I2C / IIO / Gadget …）
- Boot / FIT 镜像研究
- 后续 Rockchip BSP / RKNPU(RKNN) 研究

> ⚠️ 术语口径：本文档统一使用 **initial board support / mainline bring-up**，
> 不使用 *full support / completely supported*——显示、Wi-Fi、NPU 等功能尚未完成。

---

## 1. 项目简介

本项目记录一块粤嵌（Yueqian）定制 RK3568 开发板，从原厂 Buildroot（内核 4.19.232）
向现代 Linux 内核迁移的完整过程。板子硬件本质是 **Rockchip 官方 EVB1 DDR4 V10** 原版
（粤嵌未改动设备树），因此主线内核自带 `rk3568-evb1-v10.dts`，核心系统改动较小；
真正的硬骨头在 7 寸 MIPI-DSI 屏与外设驱动验证。

### 仓库分工（重要）

| 仓库 | 用途 |
|------|------|
| **Gecedu-RK3568**（本仓库） | 项目知识库 / 移植记录：**不保存完整 Linux kernel source** |
| **Leon19960120/linux** | 真正的 Linux 内核代码（见下方分支） |

---

## 2. 当前两条技术路线

```text
Mainline Linux 6.18
→ 学习和验证主线内核板级移植（本仓库当前主线文档）

Rockchip BSP Linux 6.6
→ 后续完整硬件、RKNPU / RKNN、产品功能路线（规划中）
```

- **Mainline 6.18 内核代码**：
  <https://github.com/Leon19960120/linux/tree/gecedu-rk3568-v6.18>
  基于 upstream Linux **v6.18**，第一笔板级支持 commit：
  `arm64: dts: rockchip: add initial support for GecEdu RK3568 board`
- **Rockchip BSP 6.6**（规划）：后续转入 `rockchip-linux/kernel` 的 `develop-6.6` /
  自有 `gecedu-rk3568-6.6` 分支，使用 Rockchip RKNPU / RKNN vendor stack。

---

## 3. 当前 Mainline 6.18 状态

| 功能 | 状态 | 说明 |
|------|------|------|
| Linux 6.18 boot | ✅ | 外置 FIT + RKDevTool 只烧 boot |
| UART console | ✅ | `ttyS2,1500000` |
| eMMC / rootfs | ✅ | 出厂 Buildroot rootfs |
| 32-bit Buildroot userspace | ✅ | 需 `CONFIG_COMPAT=y`（见 `docs/porting/mainline-6.18/04_rootfs_compat.md`） |
| Gigabit Ethernet | ✅ | `gmac1`(`fe010000`) = 当前板载以太网口 / RTL8211F-CG，1Gbps Full（`gmac0`(`fe2a0000`) = 当前 GEC 板级支持未使用，已审原理图未识别到板载 GMAC0 PHY 连接） |
| USB2 Host | ✅ | `CONFIG_PHY_ROCKCHIP_INNO_USB2=y` |
| USB3 Host | ✅ | `usb_host1_xhci`(@`fd000000`, DWC3 Host) + `combphy1`（USB3 SS phy）；本树无 `usbdp_phy` |
| USB3 Gadget kernel | ✅ | `usb_host0_xhci`(@`fcc00000`, DWC3 DRD, `dr_mode="peripheral"`+`extcon`) + `combphy0`（USB3 SS phy）；kernel gadget plumbing 已通（configfs+ffs.adb+udc），ADB userspace 见下行 |
| I2C2 | ✅ | M1，SDA GPIO4_B4 / SCL GPIO4_B5 |
| MPU6050 | ✅ | IIO，0x69（2026-08-08 确认） |
| BH1750 | ✅ | IIO，0x23，`in_illuminance_raw`（2026-08-08 确认） |
| ADB userspace | ⚠️ PAUSED | kernel gadget plumbing 已通（见 `USB3 Gadget kernel` 行），userspace `adbd` 未完成基于 FunctionFS 的启动流程（`tcp:5037` blocker） |
| Display | ⚠️ | framebuffer / display pipeline 未完成 |
| Wi-Fi RTL8723DS | ❌ | 原 4.19 的 `8723ds.ko` 无法直接用于 6.18 |
| NPU | ❌ | mainline 6.18 路线暂不继续，转 Rockchip BSP 6.6 |

> NPU 并非单纯“失败”：Mainline Linux 6.18 的 NPU 集成暂缓，后续计划转入
> **Rockchip Linux 6.6 BSP**，使用 Rockchip RKNPU / RKNN vendor stack。

---

## 4. 仓库结构

```text
GecEdu-RK3568/
├── README.md                      ← 本文件
├── LICENSE
├── docs/
│   ├── hardware/                  ← 板卡硬件资料
│   │   ├── 01_board_overview.md
│   │   ├── 02_soc_and_memory.md
│   │   ├── 03_interface_mapping.md
│   │   └── 03_keypad_test.md
│   ├── porting/
│   │   ├── README.md
│   │   ├── mainline-6.18/         ← 主线 6.18 移植文档（00~10）
│   │   └── rockchip-6.6/          ← BSP 6.6 路线（规划）
│   └── troubleshooting/           ← 分主题排障
├── porting/
│   └── mainline-6.18/
│       ├── boot/fit-image.its     ← FIT 打包描述
│       └── configs/               ← bring-up checkpoint（*.config）
├── logs/
│   └── mainline-6.18/             ← 分主题实机日志（boot/ethernet/usb/i2c）
├── hardware/Device Tree/          ← 厂内提取的 rk3568.dts / .dtb（参考）
├── scripts/                       ← 构建 / 测试脚本
├── rockchip_test/                 ← Rockchip 官方硬件测试套件
├── 辅助文档/                       ← 厂商硬件手册
└── demo/ assets/ uboot/ build/    ← 镜像 / 资源
```

---

## 5. 快速开始

### 串口调试
- 连接：USB Type-C (USB_TTL) → CH340C 转串口
- 波特率：**1500000**
- 控制台：`ttyS2`（换主线后，原厂 `ttyFIQ0` 不再使用）

### 固件烧写
进入 Loader 模式后用 Rockchip 工具烧写。参考：
[docs/porting/mainline-6.18/08_adb_gadget.md](docs/porting/mainline-6.18/08_adb_gadget.md)

### 构建内核
见 [docs/porting/mainline-6.18/02_kernel_build.md](docs/porting/mainline-6.18/02_kernel_build.md)
与 [porting/mainline-6.18/configs/](porting/mainline-6.18/configs/) 中的 working config。

---

## 6. 文档导航

- **主线 6.18 总览**：[docs/porting/mainline-6.18/00_overview.md](docs/porting/mainline-6.18/00_overview.md)
- **启动链 / FIT**：[01_boot_chain.md](docs/porting/mainline-6.18/01_boot_chain.md)
- **内核构建**：[02_kernel_build.md](docs/porting/mainline-6.18/02_kernel_build.md)
- **设备树**：[03_device_tree.md](docs/porting/mainline-6.18/03_device_tree.md)
- **rootfs 兼容**：[04_rootfs_compat.md](docs/porting/mainline-6.18/04_rootfs_compat.md)
- **以太网**：[05_ethernet.md](docs/porting/mainline-6.18/05_ethernet.md)
- **USB**：[06_usb.md](docs/porting/mainline-6.18/06_usb.md)
- **I2C / 传感器**：[07_i2c_sensors.md](docs/porting/mainline-6.18/07_i2c_sensors.md)
- **ADB Gadget**：[08_adb_gadget.md](docs/porting/mainline-6.18/08_adb_gadget.md)
- **已知问题**：[09_known_issues.md](docs/porting/mainline-6.18/09_known_issues.md)
- **调试笔记（证据链）**：[10_debug_notes.md](docs/porting/mainline-6.18/10_debug_notes.md)
- **BSP 6.6 路线**：[docs/porting/rockchip-6.6/00_overview.md](docs/porting/rockchip-6.6/00_overview.md)
- **硬件资料**：[docs/hardware/](docs/hardware/)

---

## 7. 许可证

本项目包含 Rockchip 官方测试套件（`rockchip_test/`），遵循其自带 `NOTICE` 文件中的许可条款。
其余文档以 MIT 许可证发布（见 `LICENSE`）。
