# 01 - 板卡硬件总览（Board Overview）

> 目标：用一篇把"板子是什么、有什么"说清，作为后续移植文档的起点。
> 板子本质是 Rockchip 官方 EVB 原版，粤嵌零改设备树——这是本项目难度可控的根本原因。

---

## 1. 板子身份

| 项 | 值 |
|----|----|
| 品牌 / 型号 | 粤嵌（Yueqian）**GecEdu RK3568 V1.1** 开发板 |
| 本质 | **Rockchip RK3568 EVB1 DDR4 V10** 原版（粤嵌未改设备树） |
| compatible | `rockchip,rk3568-evb1-ddr4-v10`, `rockchip,rk3568` |
| model 字符串 | `Rockchip RK3568 EVB1 DDR4 V10 Board` |
| SoC | Rockchip **RK3568**（quad-core Cortex-A55，ARMv8.2） |
| 内存 | 2 GiB **LPDDR4**（板载，DDR 训练 fwver v1.25） |
| 存储 | eMMC（约 14.7 GiB，`mmcblk1`，HS200） |
| 调试串口 | USB Type-C (USB_TTL) → CH340C，波特率 **1500000**，控制台 `ttyS2`（uart2） |

> 证据：`hardware/Device Tree/rk3568.dts`（从出厂 `boot.img` 提取反编译）的 compatible / model 字段，
> 以及 6.18 启动日志 `[ 0.000000] Machine model: Rockchip RK3568 EVB1 DDR4 V10 Board`。

---

## 2. SoC 关键资源（RK3568）

- **CPU**：4× Cortex-A55（最高 2.0 GHz，实测 `cpuinfo` 显示 min/max 816000）
- **GPU**：Mali-G52（主线 Panfrost 驱动）
- **NPU**：0.8 TOPS（RK3568 内置，主线无驱动，需 BSP 6.6 的 `rknpu`）
- **视频**：H.264/H.265 解码（rkvdec）、H.264 编码（vepu），BSP 路线更完整
- **显示**：VOP2，支持 MIPI-DSI / HDMI；本板用 7 寸 MIPI-DSI 屏
- **网络**：1× GMAC（RGMII，接 RTL8211F-CG 千兆 PHY）
- **USB**：1× Type-C（OTG/DRD，dwc3）+ USB2/USB3 Host（usbdp_phy combo）
- **其他 IP**：eMMC/SDMMC、I2C×多路、SPI、PWM、SARADC、TSADC、I2S/TDM、PCIe、声卡（RK809）

---

## 3. 接口与外围映射

板载主要外围（已核对出厂 DTS / 逆向 `rk356x-demo`）：

| 外围 | 接口 | 地址 / 总线 | 备注 |
|------|------|------------|------|
| 千兆 PHY RTL8211F | RGMII | `gmac0` @ `fe010000` | MDIO 0，reset GPIO3_B5 |
| 7" MIPI-DSI 屏 | DSI 4-lane | `dsi@fe060000` | 1024×600@60，定制 Himax IC |
| 触摸 GT911 | I2C1 | `fe5a0000` @ `0x5d` | irq GPIO3_B3 / rst GPIO3_B4 |
| 光照 BH1750 | I2C2 | `fe5b0000` @ `0x23` | IIO |
| 六轴 MPU6050 | I2C2 | `fe5b0000` @ `0x69` | IIO，中断 GPIO3_C7 |
| EEPROM 24C02 | I2C2 | `fe5b0000` @ `0x50` | 丝印 BL24C02 |
| RTC PCF8563 | I2C | — | `/dev/rtc` |
| SARADC | 片上 | `fe720000` | 供 adc-keys（4 个 ADC 按键） |
| 蜂鸣器 | GPIO | `gpio111`（GPIO2 系） | 高有效 |
| LED ×4 | GPIO | `gpio120/121/123/124` | 高有效 |
| 按键 ×6 | GPIO / ADC | `gpio_keys_polled` + `adc-keys` | 4 个 ADC 模拟 + 2 个 GPIO |
| Wi-Fi/BT RTL8723DS | SDIO + UART | `sdmmc1` + `uart8`(ttyS8) | Fn-Link FG6223 |
| CAN ×3 | — | `fe570000/fe580000/fe590000` | 出厂全 disabled，待验证 |
| 用户 USART | — | uart1/3/4/8（fe650000/fe670000/fe680000/fe6c0000） | 待板级打开 |

> 更细的脚位 / 原理图交叉核对见 `03_interface_mapping.md`；SoC 与内存细节见 `02_soc_and_memory.md`。

---

## 4. 出厂系统（4.19.232）作为基线

出厂系统是 Rockchip 官方 Buildroot（内核 4.19.232，Buildroot 2018.02-rc3），它是我们移植的**对照基线**：

- 出厂已验证可用：千兆网 1Gbps、MIPI-DSI 屏亮、GT911 触摸（但仍 3 次 i2c 探测失败）、BH1750/MPU6050、
  RTC/EEPROM/SARADC、USB（含 Type-C gadget 实际 CONFIGURED）、Wi-Fi 加载（但 NO-CARRIER）。
- 有价值的结论：**两内核都认不到触摸** → 是屏/触摸硬件或地址问题，非 6.18 独有；
  6.18 的 `dwc3 failed to init core` 更可能是 DTS/时钟/combphy 缺失而非硬件废。

---

## 5. 分区布局（来自出厂 `parameter.txt`）

```text
uboot(4M) / misc(4M) / boot(32M) / recovery(32M) / backup(32M) / rootfs(6G) / oem(128M) / userdata(剩)
```

- `boot` 分区 **32 MiB** → 这是 FIT 必须 gzip 压缩内核、且外置 FIT 头 < 4KiB 的根本约束（见 `01_boot_chain.md`）。
- 移植时**只刷 `boot` 分区**，保留 `uboot` / `rootfs` / `userdata`，风险最低、可随时回退出厂。

---

## 6. 调试入口

- 串口：1500000 8N1，控制台 `ttyS2`（换主线后不再用厂内 `ttyFIQ0`）。
- 烧写：USB Type-C 进 Loader 模式 → RKDevTool。
- 详见 `../porting/mainline-6.18/01_boot_chain.md` 与 `08_adb_gadget.md`。
