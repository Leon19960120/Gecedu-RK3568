# GecEdu RK3568 — Rockchip Linux BSP 5.10 / 6.1 移植记录

[文档站](https://leon19960120.github.io/Gecedu-RK3568/) · [GitHub 仓库](https://github.com/Leon19960120/Gecedu-RK3568)

本仓库是 **GecEdu / GEC RK3568 V11** 开发板的 Linux BSP bring-up 与板级移植知识库，记录 Device Tree 适配、内核配置、驱动集成、实机验证和问题定位过程。

本仓库 **不是完整 Linux kernel source 仓库**。完整 vendor kernel 仍放在独立的 LubanCat SDK 工作树中。

## 项目范围

| 项目 | 当前定位 |
|------|----------|
| SoC / 板卡 | Rockchip RK3568，GEC / GecEdu RK3568 V11 |
| 并行维护 BSP | Rockchip BSP Linux **5.10.209** / **6.1.99** |
| SDK | `lubancat-linux-sdk` |
| 构建入口 | `./build.sh kernel` |
| BSP 5.10 | `rockchip_rk3568_gec_defconfig` / `rk3568-gec-v11-linux.dts` |
| BSP 6.1 | `rockchip_rk3568_gec_linux_defconfig` / `rk3568-evb1-gec-v11-linux` |
| 参考路线 | Mainline Linux 6.18 bring-up |
| 暂缓路线 | Rockchip BSP Linux 6.6 研究 |

文档坚持“证据优先”：区分 source DTS、built DTB、running DTB、bus device、driver bind、subsystem register 和 runtime behavior，不因为 DTS 里 `status = "okay"` 就直接写成“功能完成”。

## 当前 BSP 状态

两条 BSP 路线同等维护，各自保留独立证据与风险边界：

- [BSP 5.10 总览](docs/porting/rockchip-5.10/00_overview.md)
- [BSP 6.1 总览](docs/porting/rockchip-6.1/00_overview.md)

本 README 不重复维护外设状态表，避免多处漂移。

## 仓库结构

```text
GecEdu-RK3568/
├── README.md
├── docs/
│   ├── hardware/                  # 板卡硬件资料与接口映射
│   ├── porting/
│   │   ├── rockchip-5.10/         # BSP 5.10 bring-up 文档
│   │   ├── rockchip-6.1/          # BSP 6.1 bring-up、裁剪与验证文档
│   │   ├── mainline-6.18/         # Mainline 参考路线
│   │   └── rockchip-6.6/          # 暂缓 / 未来研究路线
│   ├── development/               # 逆向分析与 SDK 笔记
│   └── troubleshooting/           # 分主题排障记录
├── porting/
│   ├── rockchip-5.10/             # config fragment、patch、boot 说明
│   ├── rockchip-6.1/              # 6.1 config fragment 与 boot 说明
│   └── mainline-6.18/             # Mainline FIT/config checkpoint
├── logs/
│   ├── rockchip-5.10/             # BSP 5.10 runtime 证据日志
│   ├── rockchip-6.1/              # BSP 6.1 runtime 证据日志
│   └── mainline-6.18/             # Mainline 参考日志
├── hardware/Device Tree/          # 从厂商镜像提取的 DTS 参考
├── scripts/                       # 构建与只读检查脚本
└── rockchip_test/                 # Rockchip 官方硬件测试套件
```

## 构建说明

两条 BSP 路线都在外部 LubanCat SDK 中构建，典型命令：

```bash
cd ~/lubancat-linux-sdk
./build.sh kernel
```

BSP 5.10 配置：

```text
RK_DEFCONFIG=rockchip_rk3568_gec_defconfig
RK_KERNEL_CFG=rockchip_linux_defconfig
RK_KERNEL_DTS=kernel/arch/arm64/boot/dts/rockchip/rk3568-gec-v11-linux.dts
RK_KERNEL_IMG=kernel/arch/arm64/boot/Image
```

BSP 6.1 配置：

```text
RK_KERNEL_PREFERRED="6.1"
RK_KERNEL_CFG="rockchip_rk3568_gec_linux_defconfig"
RK_KERNEL_DTS_NAME="rk3568-evb1-gec-v11-linux"
RK_USE_FIT_IMG=y
```

本仓库只保存文档、片段、diff、脚本和日志，不复制完整 vendor kernel。

## 文档入口

- [BSP 5.10 总览](docs/porting/rockchip-5.10/00_overview.md)
- [BSP 5.10 构建与启动](docs/porting/rockchip-5.10/01_build_and_boot.md)
- [BSP 5.10 Device Tree](docs/porting/rockchip-5.10/02_device_tree.md)
- [MIPI-DSI 显示](docs/porting/rockchip-5.10/03_display_mipi_dsi.md)
- [GT911 触摸屏](docs/porting/rockchip-5.10/04_touchscreen_gt911.md)
- [I2C / IIO 传感器](docs/porting/rockchip-5.10/05_i2c_iio_sensors.md)
- [RTC / EEPROM](docs/porting/rockchip-5.10/06_rtc_eeprom.md)
- [Input / PMIC / suspend](docs/porting/rockchip-5.10/07_input_pmic_suspend.md)
- [CAN](docs/porting/rockchip-5.10/08_can.md)
- [NPU](docs/porting/rockchip-5.10/09_npu.md)
- [已知问题](docs/porting/rockchip-5.10/10_known_issues.md)
- [调试方法论](docs/porting/rockchip-5.10/11_debug_methodology.md)
- [BSP 6.1 总览](docs/porting/rockchip-6.1/00_overview.md)
- [BSP 6.1 内核裁剪与验证日志](docs/porting/rockchip-6.1/05_kernel_trim_validation_log.md)
- [Mainline 6.18 参考路线](docs/porting/mainline-6.18/00_overview.md)
- [Rockchip 6.6 暂缓研究](docs/porting/rockchip-6.6/00_overview.md)

## 运行时检查脚本

两个只读脚本可用于收集当前板端状态：

```bash
sh scripts/check_bsp_5_10.sh
sh scripts/check_i2c_bindings.sh
```

它们只读取系统状态，不修改板端配置。

## 许可证

本项目包含 Rockchip 官方测试套件（`rockchip_test/`），遵循其自带 `NOTICE` 文件。其余项目文档以 MIT 许可证发布，见 [LICENSE](LICENSE)。
