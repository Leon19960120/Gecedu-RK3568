# 01 - 板卡硬件总览（Board Overview）

> ⚠️ 本页主要沉淀 FACTORY-4.19 与 MAINLINE-6.18 阶段的硬件识别结论。
> 当前现役 Bring-up 路线请以 `../porting/rockchip-5.10/` 为准；若两者冲突，按证据标签区分，不直接覆盖历史事实。

> 目标：用一篇把"板子是什么、有什么"说清，作为后续移植文档的起点。
> 板子本质是 Rockchip 官方 EVB 原版，粤嵌零改设备树——这是本项目难度可控的根本原因。

---

## 1. 板子身份

| 项 | 值 |
|----|----|
| 品牌 / 型号 | 粤嵌（Yueqian）**GecEdu RK3568 V1.1** 开发板 |
| 本质 | **Rockchip RK3568 EVB1 DDR4 V10** 原版派生产物（粤嵌未改原厂设备树，自起 `gec-v11` 板级文件） |
| compatible | 6.18 committed DTS：`rockchip,rk3568-evb1-v10`, `rockchip,rk3568`（Evidence: MAINLINE-6.18）；<br>出厂 4.19 DTB：`rockchip,rk3568-evb1-ddr4-v10`（Evidence: FACTORY-4.19） |
| model 字符串 | 6.18 committed DTS：`Rockchip RK3568 GEC V1.1 Board`（Evidence: MAINLINE-6.18）；<br>出厂 4.19：`Rockchip RK3568 EVB1 DDR4 V10 Board` |
| SoC | Rockchip **RK3568**（quad-core Cortex-A55，ARMv8.2） |
| 内存 | 2 GiB **LPDDR4**（板载，DDR 训练 fwver v1.25） |
| 存储 | eMMC（约 14.7 GiB，`mmcblk1`，HS200） |
| 调试串口 | USB Type-C (USB_TTL) → CH340C，波特率 **1500000**，控制台 `ttyS2`（uart2） |

> 证据：出厂 4.19 `hardware/Device Tree/rk3568.dts`（从出厂 `boot.img` 提取反编译）的 compatible / model 字段，
> 以及 6.18 启动日志 `[ 0.000000] Machine model: Rockchip RK3568 GEC V1.1 Board`（committed DTS `model` 已改为 GEC V1.1）。

---

## 2. SoC 关键资源（RK3568）

- **CPU**：4× Cortex-A55（最高 2.0 GHz，实测 `cpuinfo` 显示 min/max 816000）
- **GPU**：Mali-G52（主线 Panfrost 驱动）
- **NPU**：0.8 TOPS（RK3568 内置，主线无驱动，需 BSP 6.6 的 `rknpu`）
- **视频**：H.264/H.265 解码（rkvdec）、H.264 编码（vepu），BSP 路线更完整
- **显示**：VOP2，支持 MIPI-DSI / HDMI；本板用 7 寸 MIPI-DSI 屏
- **网络**：1× GMAC（RGMII，接 RTL8211F-CG 千兆 PHY）
- **USB**：1× Type-C（OTG/DRD，dwc3 `usb_host0_xhci`）+ USB2/USB3 Host（dwc3 `usb_host1_xhci`，USB3 SS phy = `combphy0`；本树无 `usbdp_phy`）
- **其他 IP**：eMMC/SDMMC、I2C×多路、SPI、PWM、SARADC、TSADC、I2S/TDM、PCIe、声卡（RK809）

---

## 3. 接口与外围映射

板载主要外围（已核对出厂 DTS / 逆向 `rk356x-demo`；Evidence 列标注来源与验证状态）：

| 外围 | 接口 | 地址 / 总线 | 备注 | Evidence |
|------|------|------------|------|----------|
| 千兆 PHY RTL8211F | RGMII | `gmac1` @ `fe010000` | MDIO 0，reset GPIO3_B5；`gmac0`(@fe2a0000) disabled | MAINLINE-6.18 ✅ 实测 |
| 7" MIPI-DSI 屏 | DSI 4-lane | `dsi@fe060000` | 1024×600@60，`panel@0` compatible `wanchanglong,w552793baa`/`raydium,rm67200` | MAINLINE-6.18 ⚠ NOT VERIFIED |
| 触摸（三层冲突） | I2C1 | committed DTS：`fe5a0000` @ `0x14`（gt1151，irq `GPIO0_B5` / rst `GPIO0_B6`）；schematic：`TP_INT→GPIO3_B3` / `TP_RST→GPIO3_B4` | DTS 与原理图 GPIO 不一致，**不强行统一** | MAINLINE-6.18 + SCHEMATIC ⚠ NEEDS VERIFICATION |
| 光照 BH1750 | I2C2 | `fe5b0000` @ `0x23` | IIO；committed DTS 无 interrupt | MAINLINE-6.18 |
| 六轴 MPU6050 | I2C2 | `fe5b0000` @ `0x69` | IIO polling 已通；**INT `GPIO3_C7` 为 SCHEMATIC 明示，committed DTS 未建模** | MAINLINE-6.18 ✅ + SCHEMATIC（INT NOT MODELED） |
| EEPROM BL24C02F | I2C2 | 原理图 U301，接 `I2C2_SDA_M1`/`I2C2_SCL_M1`；I2C 地址 NEEDS VERIFICATION（不预设 0x50） | **SCHEMATIC 明示，committed DTS 未建模**；非 invented | SCHEMATIC / NOT MODELED IN CURRENT DTS |
| RTC PCF8563 | I2C | — | `/dev/rtc`；4.19 出厂 DTB 有，6.18 DTS 待核 | FACTORY-4.19 / 待核 |
| SARADC | 片上 | `fe720000` | 供 adc-keys（4 个 ADC 按键） | FACTORY-4.19 |
| 蜂鸣器 | GPIO | `gpio111`（GPIO3_B7） | 高有效 | FACTORY-4.19 |
| LED ×4 | GPIO | `gpio120/121/123/124` | 高有效 | FACTORY-4.19 |
| 按键 ×6 | GPIO / ADC | `gpio_keys_polled` + `adc-keys` | 4 个 ADC 模拟 + 2 个 GPIO | FACTORY-4.19 |
| Wi-Fi/BT RTL8723DS | SDIO + UART | `sdmmc1` + `uart8`(ttyS8) | Fn-Link FG6223 | FACTORY-4.19 / INFERRED |
| CAN ×3 | — | `fe570000/fe580000/fe590000` | 出厂全 disabled，待验证 | FACTORY-4.19 |
| 用户 USART | — | uart1/3/4/8（fe650000/fe670000/fe680000/fe6c0000） | 待板级打开 | FACTORY-4.19 / INFERRED |

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
