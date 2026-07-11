# GecEdu RK3568 开发板项目

粤嵌 RK3568 开发板（底板 + 核心板 + 7 寸 LVDS 触摸屏），出厂系统为 Buildroot。

> 硬件实际配置：Machine model — Rockchip RK3568 EVB1 DDR4 V10

## 硬件规格

| 组件 | 规格 | 状态 | 备注 |
|------|------|------|------|
| SoC | RK3568b2 | ✅ 已验证 | 四核 Cortex-A55, 2.0 GHz |
| RAM | 2GB LPDDR4 | ✅ 已验证 | 32 位位宽 |
| 存储 | 16GB eMMC | ✅ 已验证 | `/dev/block/mmcblk2` |
| 网络 | 千兆以太网 | ✅ 已验证 | 10/100/1000M |
| USB | 3× USB 2.0 + 1× USB 3.0 + 1× OTG | ✅ 已验证 | OTG 可用于刷机 |
| 无线 | Wi-Fi 5 (Realtek 8723DS) | ✅ 已验证 | 板载，可搜索网络 |
| 视频 | HDMI 2.0 + LVDS | ✅ 可用 | LVDS 接 7 寸触摸屏幕 |
| 音频 | 耳机 + MIC + 蜂鸣器 + SPK | ✅ 可用 | PMIC 集成编解码 |
| 其他 | SIM 卡槽 / SD 卡槽 / 4G 模组接口 / mSATA | 🔍 待验证 | 功能待驱动验证 |
| 传感器 | 六轴 MPU6050 / 光环境传感器 | 🔍 待验证 | I2C 接口 |
| 串口 | 4× UART + 1× Debug UART (1500000 波特率) + 1× CAN | ✅ 已验证 | Debug 用于串口日志 |

详细硬件资源说明见 [粤嵌开发板硬件参考手册](辅助文档/粤嵌开发板硬件参考手册.md)。

## 出厂系统

- 系统：Buildroot，内核 4.19.232
- 预装 `rk356x_demo`：基于 LVGL 的嵌入式图形测试界面，直接操作帧缓冲 (`/dev/fb0`) 并控制 GPIO 和背光
- 已知可用的 UBoot 镜像：`RK3568-EVB1-V10-BUILDROOT_V1.3.0_20251220`

## 目录结构

```
GEC-RK3568/
├── README.md              ← 本文件
├── 辅助文档/               ← 硬件参考手册等文档
│   └── 粤嵌开发板硬件参考手册.md
├── docs/
│   ├── development/       ← 开发过程记录与测试文档
│   │   ├── 01_全记录.md
│   │   ├── 开发板功能测试.md
│   │   ├── 按键测试.md
│   │   ├── 解包boot.md
│   │   └── ADB模式切换到Loader模式日志.md
│   └── notes/             ← 技术笔记与排查记录
│       ├── info-version.md
│       └── 各设备相关说明.md
├── logs/                  ← 串口启动日志归档
│   ├── README.md          ← 日志目录索引（含固件版本对照表）
│   ├── 0305-DDR训练/      ← 3月5日 DDR 预加载器训�