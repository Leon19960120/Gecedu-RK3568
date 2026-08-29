# 00 - Rockchip BSP 6.1 移植总览

> 状态：`[ACTIVE BSP ROUTE / PARTIAL RUNTIME VERIFIED]`
>
> Rockchip BSP 6.1 与 Rockchip BSP 5.10 是本项目同等维护的两条路线。两者分别记录构建配置、运行证据、裁剪进展和未解决风险，不存在“6.1 被 5.10 取代”的项目口径。

## 当前定位

Rockchip BSP 6.1（`develop-6.1`，当前内核 6.1.99）具备 in-tree `rknpu`、MPP、RKISP 和 Rockchip 显示扩展，适合继续进行 GEC V11 板级适配、专用内核裁剪和显示 / USB / NPU 验证。

当前 6.1 已经不是“仅编译未运行”状态：内核可启动、GEC 专用 defconfig 生效、HDMI 和 `/dev/fb0` 已验证，USB 拓扑与部分接口也已有实测记录。不同外设仍按各自证据层级标记，不能因为系统启动成功就把全部功能写成已完成。

## 当前基线

| 项 | 值 |
|----|----|
| SDK | `~/lubancat-linux-sdk` |
| Kernel | `~/lubancat-linux-sdk/kernel-6.1` |
| 内核版本 | Rockchip BSP Linux 6.1.99 |
| BoardConfig | `RK_KERNEL_PREFERRED="6.1"` |
| 专用 defconfig | `rockchip_rk3568_gec_linux_defconfig` |
| DTS | `rk3568-evb1-gec-v11-linux` |
| FIT | `RK_USE_FIT_IMG=y` |
| 目标板 | GEC RK3568 DDR4 V11 |

早期 `/home/hyl/rockchip-kernel-6.1` 独立内核树和 `rk3568-gec-linux.dts` override 实验仍保留为技术来源；当前运行验证与后续裁剪以 LubanCat SDK 的 `kernel-6.1`、专用 defconfig 和当前 DTS 为准。

## 已验证进展

- `[BSP-6.1 RUNTIME VERIFIED]` Linux 6.1.99 可启动，4 个 Cortex-A55 CPU 正常进入系统，shell 可用。
- `[BSP-6.1 RUNTIME VERIFIED]` `rockchip_rk3568_gec_linux_defconfig` 生效，第一轮 SoC selector 与 `NR_CPUS` 裁剪已完成。
- `[BSP-6.1 RUNTIME VERIFIED]` 补齐 `CONFIG_FB=y` 后，DRM fbdev emulation 创建 `/dev/fb0`。
- `[BSP-6.1 RUNTIME VERIFIED]` HDMI EDID、PHY、VOP2 和 1920x1080@60 输出正常。
- `[BSP-6.1 RUNTIME VERIFIED]` USB3 Host、USB OTG、U601 USB2 HUB 与三个下游口已有运行时 / CH340 插拔证据；未使用的 USB2 HOST3 已完成隔离验证。
- `[BSP-6.1 RUNTIME VERIFIED]` RTL8723DS 已切换到内核自带 rtw88 模块方案，五个模块完成加载并读取 `rtw8723d_fw.bin`，板端已出现 `Firmware version 48.0.0, H2C version 0`。
- `[BSP-6.1 RUNTIME VERIFIED]` RK3568 CAN1 已由 `CONFIG_CANFD_ROCKCHIP` 驱动注册为 SocketCAN `can0`，500 kbit/s 位时序与 200 MHz 时钟已验证。
- `[BSP-6.1 RUNTIME VERIFIED]` RTL8723DS Bluetooth 已通过 RFKill、UART8/H5 和 `rtk_hciattach` 完成固件下载与 `hci0` 注册，最终串口速度为 1.5 Mbit/s。
- `[BSP-6.1 RUNTIME VERIFIED]` GPIO3_A4 / MP2315 regulator 已统一为高电平有效，编译 DTB flag 为 `GPIO_ACTIVE_HIGH`，板端原 active-low conflict warning 已消失。
- `[BSP-6.1 COMPILE VERIFIED]` GEC DTS override、触摸、I2C 传感器、Wi-Fi / BT 等板级差异已形成分层记录；各外设是否运行通过仍以对应日志为准。

## 当前开放问题

- `[PENDING]` DSI LCD 暂未完成 6.1 实机测试，不能沿用 BSP 5.10 的 DSI 已验证状态。
- `[PENDING]` LVGL 固定 1024x600 与 HDMI 1920x1080 framebuffer 的匹配，以及 VOP2 hardware scaling 方案仍待验证。
- `[OPEN]` NPU / PD_NPU warm-reset panic 的机制尚未最终确认，详见 `02_npu_pd_warm_reset.md`。
- `[PENDING]` RTL8723DS 已出现 `wlan0`，但 AP 扫描、关联、DHCP 和 ping 尚未补齐，不能把固件握手和 netdev 注册直接写成 Wi-Fi 网络功能通过。
- `[PENDING]` CAN 控制器已运行，但 LVGL CAN Test 仍需删除不受支持的 `fd on/dbitrate` 并修正反向过滤器；内部 loopback 和外部物理总线双向收发尚未验证。
- `[PENDING]` Bluetooth 的 `hci0` 仍为 `DOWN`，扫描、配对、目标 profile 和冷启动自动 attach 尚未验证。
- `[PENDING]` Goodix 已从 I2C 通信失败进展到读出 GT911 ID 并注册 input device；触摸坐标/中断实测、供电属性和可选 cfg firmware 仍待闭环。
- `[OPEN]` Linux 6.1.99 #22 完整启动日志已归档；关键字初筛 62 行，归并为 24 个问题族、0 个致命错误；其中 regulator 极性冲突已关闭，当前剩余 23 项按 `10_boot_log_issue_audit_2026-08-29.md` 推进。
- `[PENDING]` RTC 主设备选择、Type-C 反向供电和 USB warning 按长期验证日志继续推进。

NPU warm-reset 是 6.1 的重要风险，但它是一个需要继续定位的子系统问题，不用于否定整条 BSP 6.1 路线。BSP 5.10 在相同板卡上的行为可作为对照证据，两条路线的结论分别维护。

## 关键技术积累

### DTS override

6.1 当前采用 EVB1 规范命名的三层 GEC 派生结构：`rk3568-evb1-gec-v11-linux.dts`、`rk3568-evb1-gec-v11.dtsi` 和 `rk3568-evb-gec.dtsi`。共享的 `rk3568.dtsi`、`rk356x.dtsi`、`rk3568-linux.dtsi` 继续复用，板级修改落在带 `gec` 的自有文件中。文件归属按来源和职责判断，不能用 `rk3568-evb1-*` 通配符判断是否可修改。详细内容见 `01_dts_override.md`。

### 启动方法

早期自编镜像启动失败的主要原因是手动 `bootm` 搬运地址错误。改用 Rockchip 原生 `boot_fit` 和正确 FIT 打包后，6.1 已成功启动。该问题已解决，不再作为当前路线状态判断依据。

### NPU warm-reset

已观察到冷启动成功、warm reset 后可能在 `rockchip_pmu_set_idle_request` 路径触发 `panic_on_set_idle`。VDD_NPU 电压轨与 PD_NPU 电源域必须分开分析，当前机制仍是开放问题。

### 专用内核裁剪

6.1 已建立长期维护的“内核裁剪与板级验证日志”，所有 defconfig、DTS、启动日志、USB 实测和 warning 结论都应持续回写，不只保留在对话中。

## 文档入口

| 文档 | 内容 |
|------|------|
| `01_dts_override.md` | DTS 分层、板级差异与 config closure |
| `02_npu_pd_warm_reset.md` | NPU warm-reset 已观察事实、机制假设与后续取证 |
| `03_boot_verify_2026-08-24.md` | 6.1 首次运行时启动与二次 DTS 验证 |
| `04_fbdev_hdmi_lvgl_2026-08-27.md` | fb0、HDMI、LVGL 分辨率与双屏目标 |
| `05_kernel_trim_validation_log.md` | 长期内核裁剪、USB 拓扑和板级验证账本 |
| `06_usb_visual_guide.md` | USB 控制器、PHY、接口方向与排障图解 |
| `07_wifi_rtl8723ds_rtw88_2026-08-29.md` | RTL8723DS rtw88 模块、固件与联网验收流程 |
| `08_can_rk3568_2026-08-29.md` | RK3568 CAN1 驱动、DTS、SocketCAN 与物理总线验证边界 |
| `09_bluetooth_rtl8723ds_uart8_2026-08-29.md` | RTL8723DS Bluetooth RFKill、UART8、固件、HCI 与扫描边界 |
| `10_boot_log_issue_audit_2026-08-29.md` | Linux 6.1.99 #22 完整启动日志审计、24 个问题族与修复顺序 |

## 与其它路线的关系

| 路线 | 当前定位 |
|------|----------|
| `rockchip-5.10/` | 并行维护 BSP；拥有独立运行证据和外设状态 |
| `rockchip-6.1/` | 并行维护 BSP；持续推进裁剪、显示、USB 与 NPU 风险定位 |
| `mainline-6.18/` | Mainline 参考路线，用于 upstream 启动链与驱动学习 |
| `rockchip-6.6/` | 暂缓研究，尚无对应的当前板端运行结论 |

两条 Rockchip BSP 路线之间可以互相复用方法和对照证据，但不得直接复制状态。例如 BSP 5.10 的 DSI LCD 已验证，不等于 BSP 6.1 的 DSI LCD 已验证；BSP 6.1 的 USB 裁剪结论也应保留自己的实验记录。
