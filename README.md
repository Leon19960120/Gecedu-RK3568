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
├── LICENSE                ← MIT 许可证
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
│   ├── 0305-DDR训练/      ← 3月5日 DDR 预加载器训练日志
│   ├── 0306-UBoot启动与故障/ ← 3月6日完整启动流程与故障记录
│   ├── 0307-对比参考/     ← 正常板基准日志
│   ├── 硬件替换调试/      ← 更换 boot/UBoot 等组件后的对比
│   └── 新版本固件/        ← DDR v1.25 最新预加载器日志
├── hardware/
│   └── Device Tree/       ← 设备树文件
│       ├── rk3568.dts
│       └── rk3568.dtb
├── scripts/
│   └── power-key.sh       ← 电源键测试脚本
├── demo/
│   └── rk356x-demo_good_board_backup  ← LVGL 图形测试界面备份
├── uboot/                 ← UBoot 镜像
│   └── uboot.img
├── build/
│   └── MiniLoaderAll.bin  ← 预加载器二进制
├── rockchip_test/         ← Rockchip 官方硬件测试套件
│   ├── rockchip_test.sh   ← 总控脚本
│   ├── NOTICE             ← 测试套件说明
│   ├── audio/             ← 音频测试
│   ├── auto_reboot/       ← 自动重启测试
│   ├── bluetooth/         ← 蓝牙测试
│   ├── camera/            ← 摄像头测试
│   ├── cpu/               ← CPU 测试
│   ├── ddr/               ← DDR 测试
│   ├── flash_test/        ← 闪存测试
│   ├── gpu/               ← GPU 测试
│   ├── recovery_test/     ← Recovery 测试
│   ├── suspend_resume/    ← 休眠唤醒测试
│   ├── video/             ← 视频测试
│   └── wifi/              ← Wi-Fi 测试
└── assets/                ← 图片资源
    └── IMG_2742.JPG
```

## 快速开始

### 串口调试

- 连接方式：USB Type-C (USB_TTL) → CH340C 转串口
- 波特率：1500000
- OTG 接口可用于固件烧写

### 固件烧写

通过 OTG 接口将开发板进入 Loader 模式，使用 Rockchip 刷机工具烧写镜像。
参考：[ADB 模式切换到 Loader 模式日志](docs/development/ADB模式切换到Loader模式日志.md)

### 硬件测试

```bash
# 运行完整硬件测试套件
./rockchip_test/rockchip_test.sh

# 或单独测试某项
cd rockchip_test/audio
cd rockchip_test/wifi
# ...
```

## 固件版本演进

| 固件版本 | 日期 | 说明 |
|---------|------|------|
| DDR V1.13 | 2022-02-18 | 早期预加载器 |
| DDR V1.16 | 2023-03-02 | 中期版本 |
| DDR V1.18 | 2023-07-17 | 广泛使用 |
| DDR v1.25 | 2025-12-03 | 最新预加载器 (`5b48980fd7`) |

## 调试记录

### DDR 训练日志 (2026-03-05 ~ 03-07)

3 月初对开发板进行了系统的 DDR 训练调试，记录了从 V1.13 到 v1.25 多个固件版本的训练数据，对比了正常板与问题板的差异。详见 [logs/README.md](logs/README.md)。

### GPIO 资源

| 引脚 | 功能 |
|------|------|
| GPIO 111 | 蜂鸣器 |
| GPIO 120-124 | 用户 LED |
| GPIO 40/42 | 按键 UP/DOWN |
| GPIO 73-84 | 蓝牙控制 |
| GPIO 98 | 功放控制 (spk-ctl) |

## 许可证

本项目包含 Rockchip 官方测试套件 (`rockchip_test/`)，遵循其自带的 NOTICE 文件中的许可条款。
