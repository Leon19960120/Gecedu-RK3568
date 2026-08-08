# docs/porting — 移植文档索引

本目录存放 Linux 内核移植相关文档。完整内核源码在外部仓库
**Leon19960120/linux**（分支 `gecedu-rk3568-v6.18`，基于 upstream v6.18），本仓库只保留移植记录与配置。

## mainline-6.18/ — 主线内核 6.18 移植（当前主线，已验证）

| 文件 | 内容 |
|------|------|
| `00_overview.md` | 移植总览：base / SoC / board / kernel fork / 当前 DTS 定位 |
| `01_boot_chain.md` | 启动链与 FIT 兼容（旧 Rockchip U-Boot 的 `-E -p 0x800` 坑）+ 出厂 boot.img 解包证据 |
| `02_kernel_build.md` | 交叉编译环境与 DTS 编译、working config 位置 |
| `03_device_tree.md` | 板级 DTS 适配与已确认映射（GMAC/USB/I2C/触摸/背光） |
| `04_rootfs_compat.md` | 64-bit kernel + 32-bit AArch32 userspace（`CONFIG_COMPAT`） |
| `05_ethernet.md` | GMAC / RTL8211F 千兆以太网 bring-up（✅ 1Gbps） |
| `06_usb.md` | USB2 / USB3（DWC3 + `combphy0`(@fcc00000 host0)/`combphy1`(@fd000000 host1) 提供 SS phy；**无 `usbdp_phy`**），含 xhci 死循环（SUPERSEDED 诊断手段）|
| `07_i2c_sensors.md` | I2C2 / MPU6050 / BH1750（✅ 已验证）；MPU6050 INT(GPIO3_C7)/EEPROM 为 SCHEMATIC、**NOT MODELED IN CURRENT DTS** |
| `08_adb_gadget.md` | USB Gadget（kernel path works，userspace adbd 未收口） |
| `09_known_issues.md` | 未解决问题清单（显示 / Wi-Fi / NPU / CAN / USART …） |
| `10_debug_notes.md` | 调试笔记（按"问题→现象→假设→验证→结论"记录，保留错误假设） |

## rockchip-6.6/ — Rockchip BSP 6.6 路线（规划中，未实测）

| 文件 | 内容 |
|------|------|
| `00_overview.md` | 为什么从 mainline 6.18 转 BSP 6.6 / 获取方式 / DTS 计划 / WiFi 专项 |
| `01_bsp_setup.md` | BSP 内核获取与构建（规划） |
| `02_board_dts.md` | 板级 DTS 移植计划（规划） |
| `03_rknpu_rknn.md` | RKNPU 驱动 / RKNN Runtime / Toolkit2 / NPU 验证计划（规划） |

> ⚠️ `rockchip-6.6/` 下除 `00_overview.md`（含已核实的方向变更事实）外均为**规划**，
> 未实测成功前不写为"已完成"。

## 相关配置（仓库根级 `porting/`）

- `porting/mainline-6.18/boot/fit-image.its` — FIT 打包描述
- `porting/mainline-6.18/configs/` — bring-up checkpoint（`*.config`），
  `rk3568-gec-v11-latest-working.config` 为当前最新实机验证配置，`history/` 为历史 checkpoint。

## 其它参考（保留，未删除）

- `panel-himax-evb1.c` — 屏面板 `drm_panel` 驱动骨架（mainline 路线用；BSP 路线不需要）
- `rk3568-evb1-v10-panel.dts` — 屏 DTS 接线片段（含 pwm5 修正）

## 硬件与排障

- 硬件资料：`docs/hardware/`（01_board_overview / 02_soc_and_memory / 03_interface_mapping）
- 分主题排障：`docs/troubleshooting/`（boot / ethernet / usb / i2c）
