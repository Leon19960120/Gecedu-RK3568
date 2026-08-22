# 00 - Rockchip BSP 5.10 移植总览

> 状态：**当前现役路线**  
> 证据模型：统一使用 `[BSP-5.10 RUNTIME VERIFIED]`、`[BSP-5.10 DTS VERIFIED]`、`[PENDING]`、`[NEEDS VERIFICATION]`、`[SUPERSEDED]` 等标签。

## 范围

本目录记录 GecEdu RK3568 V11 在 Rockchip BSP Linux 5.10.209 上的当前移植进度，构建环境基于 LubanCat SDK。

本仓库只保存笔记、配置片段、diff 和日志。完整 SDK / kernel source 仍保留在本仓库之外。

## 当前基线

| 项目 | 值 |
|------|----|
| SoC | Rockchip RK3568 |
| 板卡 | GEC / GecEdu RK3568 V11 |
| 运行时 model | `Rockchip RK3568 GEC DDR4 V10 Board` |
| 内核 | Rockchip BSP Linux 5.10.209 |
| SDK | `lubancat-linux-sdk` |
| 构建入口 | `./build.sh kernel` |
| 板级配置 | `rockchip_rk3568_gec_defconfig` |
| 内核配置基线 | `rockchip_linux_defconfig` |
| 当前 DTS | `rk3568-gec-v11-linux.dts` |

## 已验证功能

- `[BSP-5.10 RUNTIME VERIFIED]` 内核可启动，运行时 model 为 GEC 板。
- `[BSP-5.10 RUNTIME VERIFIED]` UART 调试控制台 `ttyFIQ0`（波特率 1500000）。
- `[BSP-5.10 RUNTIME VERIFIED]` eMMC 以 HS200 模式枚举，分区可用。
- `[BSP-5.10 RUNTIME VERIFIED]` MIPI-DSI LCD 已完成 U-Boot logo、DRM bind、`fb0`、背光和 1024x600p60 link。根因修复点是 `route_dsi0` 回到 VP0，避免与 HDMI route 抢 VP1。
- `[BSP-5.10 RUNTIME VERIFIED]` SARADC、MPU6050、BH1750 已验证：`inv-mpu6050-i2c 2-0069`、`bh1750 2-0023`（IIO `iio:device2`，属性为 `in_illuminance_raw`）均 probe。
- `[BSP-5.10 RUNTIME VERIFIED]` RK809 RTC、PCF8563 RTC、24C02 EEPROM 已确认。
- `[BSP-5.10 RUNTIME VERIFIED]` GT911 触摸屏在 I2C1 `0x5d` probe，`ID 911, version 1060`，注册 input 设备（`Goodix Capacitive TouchScreen`）。
- `[BSP-5.10 RUNTIME VERIFIED]` RK809 PowerKey 可产生 `KEY_POWER`，deep suspend entry 已进入。
- `[BSP-5.10 RUNTIME VERIFIED]` RTL8211F Ethernet、USB2/USB3、GPU Mali、Audio 均已起来。
- `[BSP-5.10 RUNTIME VERIFIED]` RTL8723DS 的 SDIO 控制器、电源时序、`8723ds.ko` 模块加载和 `wlan0` / `p2p0` 注册已通。
- `[BSP-5.10 RUNTIME VERIFIED]` RKNPU kernel driver probe 与 IOMMU path 已通。

## 待验证功能

- `[PENDING]` RTL8723DS Wi-Fi 仍需验证扫描、关联和 DHCP；驱动加载与网卡注册已经成功。
- `[PENDING]` BT：`[BT_RFKILL]` 已解析 GPIO 并注册 `bt_default`，通用 `hci_uart`（H4/H5）已加载；但 `hci0` 未创建、Realtek RTL / UART8 绑定未完成。
- `[PENDING]` CAN1 已出现 CAN device driver interface，仍需 `ip link` 确认 `can0/can1` 并做 SocketCAN 实际收发。
- `[PENDING]` NPU 用户态 RKNN 推理仍需单独验证。
- `[PENDING]` deep suspend 的完整 wakeup 路径仍需验证（entry 已验证）。
- `[PENDING]` Camera 链：需真实 sensor 采集跑通才能标记 verified；EVB sensor 报错作为板级差异记录。
- `[NEEDS VERIFICATION]` Headset 与 RK817 battery / charger warning 需要最终硬件和 DTS 决策。

## 历史路线关系

Mainline 6.18 仍作为历史学习路线保留。Rockchip BSP 6.6 作为暂缓研究路线保留。二者都不应被删除，也不应被改写为 BSP 5.10 的运行事实。
