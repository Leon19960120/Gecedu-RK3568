# 10 - Linux 6.1.99 #22 启动日志问题审计

> 状态：`[BOOT SUCCESS / 24 OBSERVED / 1 RESOLVED / 23 OPEN / 0 FATAL]`
>
> 审计对象：`Linux 6.1.99 #22 SMP Sat Aug 29 15:51:58 CST 2026`
>
> 原始证据：`logs/rockchip-6.1/boot/kernel_boot_2026-08-29_kernel-6.1.99-22.log`

## 结论

这次启动是成功的，不存在阻止内核进入用户空间的致命错误：4 个 CPU 已启动，eMMC HS200 与 rootfs 正常，DRM 创建 `fb0`，HDMI、千兆以太网、USB、GPU、NPU 驱动注册、CAN 和后续 Bluetooth attach 均有继续运行的证据。

不能把所有包含 `error`、`failed`、`not found` 的行都逐行算成故障。按统一关键字初筛，690 行原始日志中有 62 行问题型文本；去掉重复行、同一驱动连续打印和已有 fallback 的信息后，共归并为 **24 个问题族**。2026-08-29 后续修复已关闭其中 1 项，当前按本审计剩余 23 项未闭环：

| 类别 | 数量 | 含义 |
|------|------|------|
| P0 致命 | 0 | 没有 panic、oops、rootfs 挂载失败或 init 启动失败 |
| P1 功能闭环 | 5 | 当前项目应优先验证或修复的功能问题 |
| P2 配置完整性 | 8（1 已解决，7 未闭环） | 不阻止启动，但会影响目标功能、稳定性或量产一致性 |
| P3 可选 / 清理 | 11 | 已有 fallback，或只在启用对应功能时需要处理 |

统计命令口径如下，数字只用于筛选，不直接代表故障数：

```shell
dmesg | grep -iE "error|failed|can't|unable|invalid|illegal|missing|not found|not set|not active|dummy regulator|deferred probe|no medium"
```

## 已确认正常的主链路

| 子系统 | 后续成功证据 | 当前结论 |
|--------|--------------|----------|
| CPU / SMP | 4 个 Cortex-A55 启动 | 正常 |
| eMMC / rootfs | `mmc0: new HS200 MMC card`、rootfs 挂载、`Run /sbin/init` | 正常 |
| Ethernet | RTL8211F，`Link is Up - 1Gbps/Full` | 正常 |
| DRM / fbdev | VOP2、HDMI、DSI 组件绑定，`fb0` 创建 | 框架正常；DSI LCD 未实测 |
| GPU | 使用 fallback power model 后 `Probed as mali0` | 驱动正常，功耗模型待完善 |
| NPU | IOMMU 启用、`Initialized rknpu 0.9.8` | 驱动注册，不等于 RKNN workload 通过 |
| Goodix | 读出 `ID 911` / `version 1060`，注册 input3 | probe 已成功，触摸坐标实测待补 |
| SDIO Wi-Fi | `mmc2: new high speed SDIO card` | SDIO 枚举正常；联网仍待闭环 |
| CAN | 后续 `can0` link ready | 控制器已运行；物理总线收发待补 |
| Bluetooth | UART8 中断模式 fallback 后 HCI attach 已完成 | DMA 不是当前阻断项 |

## 24 个问题族

### P1：优先完成的 5 项

| # | 问题族 | 日志证据与判断 | 解决路线 |
|---|--------|----------------|----------|
| 1 | DSI panel 描述不完整且 LCD 未实测 | `not found firmware desc data`、`Expected bpc in {6,8} but got: 0`；DSI 框架绑定不能代替屏幕点亮验证 | 暂不改 route；接上 1024x600 LCD 后先采集 DRM summary，再核对 `simple-panel-dsi` binding/source，确认后在 GEC panel 节点补 `bpc = <8>` 等明确属性并复测 |
| 2 | Wi-Fi 缺少 `regulatory.db` | cfg80211 证书已加载，但 `/lib/firmware/regulatory.db` 不存在；会影响法规域和信道策略 | 将与内核配置匹配的 wireless-regdb 纳入 rootfs，检查是否要求签名，然后完成 `iw reg get`、扫描、关联、DHCP 和 ping |
| 3 | Goodix 仅完成 probe，功能未闭环 | 已从旧日志的 I2C `-6` 进展到读出 GT911 ID 并注册 input；当前仍缺 AVDD28/VDDIO 描述和可选 `goodix_911_cfg.bin` | 先用 `evtest` 验证中断、坐标与方向；功能正常时再依据原理图补 supply，只有确需外部配置时才加入 cfg 文件 |
| 4 | RKISP camera pipeline 未就绪 | `can't request region`、entity 未初始化、`update sensor failed`，没有完成 sensor graph | 若项目需要相机，按 sensor -> DPHY -> CSI2 -> ISP 逐段核对 endpoint、资源和供电；若当前板型不使用相机，则关闭 GEC 派生层中整条未使用 pipeline，避免半启用 |
| 5 | NPU 仅注册，workload 与 warm-reset 未闭环 | `can't request region`、`IRQ npu_irq not found` 后驱动仍初始化；此前还有 warm-reset 风险 | 对比 6.1 原生 EVB1 的 NPU 节点，检查是否被旧 overlay 重复描述；先跑 RKNN sample，再做冷启动 / warm reset 对照，保留完整串口日志 |

### P2：配置完整性的 8 项

| # | 问题族 | 当前影响 | 解决路线 |
|---|--------|----------|----------|
| 6 | USB2PHY1 `illegal mode` | 两次稳定出现，但 xHCI/EHCI/OHCI 和 U601 HUB 继续工作 | 保持当前已验证拓扑，给 PHY 驱动临时加 mode/submode 与调用栈日志，定位调用者后再改 DTS |
| 7 | `oem` / `userdata` 分区名不匹配 | init 脚本打开 `/dev/block/by-name/oem`、`userdata` 失败 | 用 `/proc/partitions` 和 `/dev/block/by-name` 对照 parameter；决定是补分区，还是删除 rootfs 中不适用于当前布局的挂载动作 |
| 8 | suspend 配置缺失 | `pwm-regulator-config`、mem-lite / mem-ultra sleep/wakeup 未配置；普通启动不受影响 | 先确认产品是否需要 suspend-to-RAM；需要时从同 BSP、同 PMIC 的 RK3568 EVB1 参考节点移植最小配置并做串口唤醒测试 |
| 9 | `mtd_vendor_storage` 一直 deferred | eMMC 启动下可能没有该驱动期待的 MTD 后端 | 查 MAC、SN、校准数据是否依赖 vendor storage；不用则关闭对应节点/配置，需要则补实际后端，不为消日志盲目删除 |
| 10 | PCIe / 4G5G regulator 极性冲突 `[VERIFIED RESOLVED]` | 原理图确认 GPIO3_A4 直接控制 MP2315 高有效 EN；DTS 与编译 DTB 均已改为 `GPIO_ACTIVE_HIGH` | 新镜像中连续三次检索原 warning 均为空；详见 `logs/rockchip-6.1/power/pcie_4g5g_regulator_polarity_2026-08-29.md` |
| 11 | kernel logo reserved memory 未 4K 对齐 | `route-hdmi` 取 logo offset 失败，但后续 `fb0` 正常 | 区分 U-Boot logo 与 kernel loader logo；核对打包后的 reserved-memory 起始和 size，均按 0x1000 对齐后复测 HDMI/DSI |
| 12 | SDIO pinctrl / 电压 / ref clock 告警 | mmc2 最终 50 MHz 枚举 RTL8723DS，说明不是当前阻断项 | 对照 8723DS 原理图确认是否真的有独立 32 kHz/ref clock；检查 default/idle pinctrl 和 OCR 电压范围，不虚构不存在的时钟 |
| 13 | VOP2 / HDMI / DMC 可选资源不完整 | vp2 无 plane、两个 overlay plane 初始化失败、HDMI IRQ index 1 缺失、DMC 缺 VOP 映射；HDMI/fb0 仍工作 | 用 `modetest` 和 DRM debugfs 确认实际使用的 VP0/VP1、plane 与中断；只补目标显示路径需要的资源 |

### P3：可选功能和清理项 11 项

| # | 问题族 | 当前判断 |
|---|--------|----------|
| 14 | FIQ debugger 缺 fiq/wakeup IRQ | NMI handler 未安装，但 `ttyFIQ0` 注册且 console 正常；开发串口可用时低优先级 |
| 15 | 两个 backlight 缺 `power-supply` | 使用 dummy regulator；还需确认 DSI1 disabled 时是否应继续实例化 `backlight1` |
| 16 | SCMI protocol 22 / 17 inactive | 基础 SCMI v2.0 仍工作；先查固件是否支持对应协议，再决定禁用消费者或升级固件 |
| 17 | GMAC 缺 `eth_lpi` IRQ / PHY supply | RTL8211F 已 1 Gbit/s link up；LPI/WoL 或 PHY 电源门控需要时再补 |
| 18 | RK817 battery / charger 无子节点 | 无电池板型可裁对应功能，但不能删除 RK809/RK817 共用的 PMIC、RTC、codec 核心驱动 |
| 19 | AT24 / MPU6050 缺 supply | 两者继续 probe；按原理图补真实供电 rail 可消除 dummy regulator |
| 20 | MPP leakage / shared NIU reset 缺失 | 编解码器 probe 完成；在做 VPU workload 和 DVFS 前处理 |
| 21 | Mali simple power model 缺参数 | 驱动使用 fallback 并注册 mali0；GPU workload 正常前不算驱动失败 |
| 22 | RK817 codec DMA mask 未设置 | ALSA HDMI 与 RK809 codec 已注册；以播放/录音回归为准 |
| 23 | UART8 缺 DMA 属性 | 驱动自动回退中断模式，Bluetooth HCI 已可注册；吞吐或功耗需要时再补 DMA |
| 24 | udev 规则引用不存在的 `kvm` group | 创建 `kvm` group，或在未启用 KVM 时移除对应 udev rule |

## 不计入 24 项的问题型文本

以下信息在当前启动方式下属于预期、能力声明或已有明确 fallback，不作为独立故障：

- `UEFI not found`：当前通过 U-Boot / FIT / DT 启动，不依赖 UEFI。
- `DMI not present or invalid`：ARM64 板级信息来自 Device Tree。
- `Unable to detect cache hierarchy`：不影响 4 核启动和基本运行，后续可与固件/PPTT 一起研究。
- `Fixed dependency cycle(s)`：设备链接处理信息；相关设备后续已 probe。
- `LUN: removable file: (no medium)`：USB Mass Storage gadget 没配置 backing file 时符合预期。
- `No Safety Features support found`：GMAC 能力声明，不是链路失败。
- `SMCCC SOC_ID not implemented`：固件没有实现可选 SOC_ID 调用。

## 建议处理顺序

### 第一阶段：不重编内核即可验证

```shell
# 保存本轮基线
uname -a
dmesg > /tmp/dmesg-6.1.99-22.txt
cat /proc/partitions
ls -l /dev/block/by-name 2>/dev/null

# Wi-Fi regulatory database
zcat /proc/config.gz 2>/dev/null | grep -E 'CFG80211_(INTERNAL_REGDB|REQUIRE_SIGNED_REGDB|USE_KERNEL_REGDB_KEYS)'
ls -l /lib/firmware/regulatory.db*
iw reg get

# Goodix 已注册后的真实输入验证
grep -A8 -B2 -i goodix /proc/bus/input/devices
evtest /dev/input/eventX

# 分区脚本来源
grep -RsnE '/dev/block/by-name/(oem|userdata)' /etc/init.d /etc/fstab* 2>/dev/null
```

### 第二阶段：按功能逐项改 GEC DTS

一次只改一个问题族，每轮都重新生成 DTB、烧录并保存完整启动日志。优先顺序建议为：

1. 接入 DSI LCD 后确认 panel/bpc、VP0 route 和背光。
2. PCIe / 4G5G regulator 极性已修复；实际 `4G5G_3V6` 电压、always-on 策略和模块枚举另行验证。
3. 根据产品需求选择“补全 camera graph”或“关闭未使用 RKISP pipeline”。
4. 对比 6.1 原生 EVB1，消除 NPU 的重复资源描述，再跑 RKNN。
5. 最后处理 MPP、GPU power model、SCMI、suspend 等性能/低功耗项。

### 第三阶段：统一验收

```shell
# 显示
cat /sys/kernel/debug/dri/0/summary 2>/dev/null
modetest -M rockchip -c -p 2>/dev/null

# 相机
media-ctl -p 2>/dev/null
v4l2-ctl --list-devices 2>/dev/null

# NPU
dmesg | grep -iE 'rknpu|npu|iommu|power.domain|panic'
ls -l /dev/dri/renderD* /dev/rknpu* 2>/dev/null
# 随后运行与当前 librknnrt 匹配的 RKNN sample，并分别记录冷启动和 warm reset。

# 复查剩余告警
dmesg | grep -iE "error|failed|can't|unable|invalid|illegal|missing|not found|not set|deferred probe"
```

## 本轮边界

本轮只完成日志归档、问题归并和解决路线设计，没有修改 DTS、内核配置、rootfs 或镜像，也没有新增板端功能测试。后续任何一项只有在“修改 -> 编译 -> 烧录 -> 启动 -> 功能实测 -> 完整日志”闭环后，才能从 `[OPEN]` 改为 `[VERIFIED]`。
