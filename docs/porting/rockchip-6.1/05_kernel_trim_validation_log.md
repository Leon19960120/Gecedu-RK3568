# 05 - 内核裁剪与板级验证日志

> 状态：`[ACTIVE LOG]`
>
> 本文件用于持续记录 GEC RK3568 DDR4 V11 在 LubanCat Linux 6.1 内核上的裁剪、验证与回退依据。它不是一次性结论，而是后续每轮 `defconfig` / DTS / 启动日志 / `/proc` / `/sys` / DRM / ALSA / USB / regulator 等证据进入项目后的长期账本。

## 基线信息

| 项 | 当前值 |
|----|----|
| SDK | `~/lubancat-linux-sdk` |
| Kernel | `~/lubancat-linux-sdk/kernel-6.1` |
| 目标板 | GEC RK3568 DDR4 V11 |
| Machine model | `Rockchip RK3568 GEC DDR4 V11 Board` |
| 内核版本 | Rockchip vendor Linux 6.1.x |
| 板级 DTS | `rk3568-evb1-gec-v11-linux` |
| BoardConfig | `RK_KERNEL_PREFERRED="6.1"` |
| BoardConfig | `RK_KERNEL_CFG="rockchip_rk3568_gec_linux_defconfig"` |
| BoardConfig | `RK_KERNEL_DTS_NAME="rk3568-evb1-gec-v11-linux"` |
| 维护 defconfig | `arch/arm64/configs/rockchip_rk3568_gec_linux_defconfig` |

该 defconfig 最初来自通用 Rockchip 配置，目前正在逐步收敛为 GEC V11 专用配置。

## 总体原则

裁剪目标不是“尽可能少”，而是在保证板载硬件和开发调试能力的前提下，删除与 GEC V11 无关的通用驱动，降低 `kernel` / `boot.img` 体积、无意义 probe、启动日志噪声和潜在攻击面。

长期遵守一句话：

```text
先证明它不用，再删除。
```

禁止做法：

- 只凭 `CONFIG` 名称判断是否保留。
- 只凭通用 RK3568 经验代替 GEC V11 硬件事实。
- 因为驱动名里有 RK817，就认定板子必须有 RK817。
- 因为板载 CH340，就认定 RK3568 Linux 必须开启 `CONFIG_USB_SERIAL_CH341`。
- 因为启动日志出现 warning，就直接删除对应子系统。
- 一轮删除大量互相关联的关键配置。
- 未烧录、未启动、未功能验证就宣称裁剪成功。

## 判断证据顺序

每个配置项是否保留，尽量按下面顺序判断：

1. 原理图 / BOM
2. 板级 DTS / DTSI
3. Linux 启动日志
4. `/sys`
5. `/proc`
6. `lsusb` / `lspci` / `i2cdetect` / ALSA / DRM 等运行时信息
7. 内核源码实际依赖
8. 一般经验

如果证据冲突，标记为 `[PENDING]`，不要猜。

## 每轮裁剪流程

每轮只处理一个功能组，例如 Bluetooth、USB Serial、RTC、Audio、HDMI RX、RK628、camera、filesystem、regulator、GPU、NPU、input、debug、network、codec、USB gadget。

固定流程：

1. 修改 `defconfig`
2. 重新生成 `.config`
3. `grep CONFIG_xxx .config` 检查最终生效状态
4. 编译
5. 烧录
6. 检查启动日志
7. 检查对应硬件功能
8. 判定通过、失败或待确认
9. 更新本日志

注意：`defconfig` 只是输入，最终以 `.config` 为准。Kconfig 依赖可能会把已经从 defconfig 删除的配置重新打开。

当前阶段不要频繁 `savedefconfig`。等配置基本稳定后，再用它做最终显式配置收敛。

## 风险等级

| 风险 | 含义 |
|------|------|
| 低风险 | 明确没有对应硬件，且与当前工作链路无依赖 |
| 中风险 | 大概率不用，但可能影响开发调试或共享驱动 |
| 高风险 | 涉及 PMIC、clock、regulator、DRM、VOP、MMC/eMMC、rootfs、CPU DVFS、GPU、NPU、IOMMU、DMA、USB controller、核心音频总线 |

提出裁剪建议时必须写清：状态、风险、原因、证据、可能影响、修改方法、验证命令、失败回退方法。

## 已验证保留项

### CPU / SMP

状态：`[VERIFIED KEEP]`

- 当前 SoC：RK3568
- 已确认只保留 `CONFIG_CPU_RK3568=y`
- 已确认 `CONFIG_NR_CPUS=4`
- 板端运行时已确认 CPU0-CPU3 正常启动，共 4 核

后续不要恢复 PX30、RK1808、RK3328、RK3399、RK3528、RK3562、RK3576、RK3588 等其他 SoC selector，除非出现明确依赖证据。

### UART / 调试串口

状态：`[VERIFIED KEEP]`

当前已验证：

```text
CONFIG_SERIAL_8250_NR_UARTS=10
CONFIG_SERIAL_8250_RUNTIME_UARTS=10
```

运行时确认存在：

```text
ttyS0
ttyS1
ttyS4
ttyS8
```

RK3568 侧板载调试串口依赖的是 UART 控制器，不是 USB Serial Host 驱动。核心配置必须保留：

```text
CONFIG_SERIAL_8250=y
CONFIG_SERIAL_8250_CONSOLE=y
CONFIG_SERIAL_8250_DW=y
CONFIG_SERIAL_OF_PLATFORM=y
```

### framebuffer / DRM / HDMI / DSI

状态：`[VERIFIED KEEP]`

Linux 6.1 上曾出现 `/dev/fb0` 不存在、LVGL 黑屏。最终确认 Rockchip DRM fbdev emulation 需要基础 `CONFIG_FB=y`，补齐后日志出现：

```text
[drm] fb0: rockchipdrmfb frame buffer device
```

LVGL 已能打开 framebuffer。当前必须保留：

```text
CONFIG_FB=y
CONFIG_DRM=y
CONFIG_DRM_KMS_HELPER=y
CONFIG_DRM_FBDEV_EMULATION=y
CONFIG_DRM_FBDEV_OVERALLOC=100
CONFIG_DRM_ROCKCHIP=y
CONFIG_ROCKCHIP_DW_HDMI=y
CONFIG_ROCKCHIP_DW_MIPI_DSI=y
CONFIG_DRM_PANEL_SIMPLE=y
CONFIG_DRM_DW_HDMI_I2S_AUDIO=y
```

当前已验证 HDMI 可通过 EDID 识别并输出 1920x1080@60。DSI LCD 仍需实机复测，显示子系统暂不做激进裁剪。

### HDMI OUT 与 HDMI RX

状态：`[RULE]`

必须区分：

```text
CONFIG_ROCKCHIP_DW_HDMI        # HDMI 显示输出
CONFIG_VIDEO_ROCKCHIP_HDMIRX   # HDMI 输入采集
```

GEC V11 需要 HDMI 输出不等于需要 HDMI RX。若确认板卡没有 HDMI 输入采集硬件，`CONFIG_VIDEO_ROCKCHIP_HDMIRX` 可作为裁剪候选。

### Audio

状态：`[VERIFIED KEEP]`

板端 ALSA 已确认：

```text
card 0: rockchip,hdmi
card 1: rockchip,rk809-codec
```

实际音频结构：

```text
RK3568 I2S
  -> HDMI Audio
  -> RK809 internal codec
       -> playback
       -> capture
```

日志或 ALSA 中出现 `rk817-hifi` / `rk817-codec` 不代表板子有 RK817。RK809 与 RK817 共用部分 codec 驱动实现，因此不能因为名字带 RK817 就删除：

```text
CONFIG_SND_SOC_RK817=y
```

已验证删除部分 ES 系列、RT56xx、MAX98090 及其他无关 SoC 音频配置后，`rockchip,hdmi` 与 `rockchip,rk809-codec` 仍可正常注册。

### RTC

状态：`[VERIFIED KEEP / PENDING MAIN RTC]`

板子存在两个 RTC：

```text
rtc0: RK809 internal RTC
rtc1: PCF8563
```

已观察：

```text
rtc0 时间: 2017-08-04
rtc1 时间: 2026-08-27
system date: 2017-08-04
```

说明当前系统启动时使用 `rtc0` 校时，而 PCF8563 本身时间正确。PCF8563 位于 I2C bus 0，地址 `0x51`，驱动必须保留：

```text
CONFIG_RTC_DRV_PCF8563=y
```

曾出现 `rtc rtc1: invalid alarm value`，清理 alarm 后重启已消失；`/sys/class/rtc/rtc1/wakealarm` 为空属于正常状态。

后续可以单独研究是否关闭 `CONFIG_RTC_DRV_RK808`，让 PCF8563 成为主 RTC。该操作风险为中到高，必须独立验证。

### CH340 / USB Serial Host / USB Gadget Serial

状态：`[RULE]`

GEC V11 板载 CH340 连接方向是：

```text
PC USB -> CH340 -> RK3568 UART RX/TX
```

CH340 是 PC 侧看到的 USB Device，驱动由连接开发板的 Windows/Linux PC 加载。RK3568 侧只看到 UART，因此不能因为开发板上焊有 CH340，就认为 RK3568 Linux 必须开启：

```text
CONFIG_USB_SERIAL_CH341=y
```

`CONFIG_USB_SERIAL` 属于 RK3568 作为 USB Host 时识别外接 USB 转串口设备，例如外接 CH340、CP210x、FTDI、PL2303：

```text
CONFIG_USB_SERIAL=y
CONFIG_USB_SERIAL_CH341=y
CONFIG_USB_SERIAL_CP210X=y
CONFIG_USB_SERIAL_FTDI_SIO=y
CONFIG_USB_SERIAL_PL2303=y
```

USB Gadget Serial 是相反方向，即 RK3568 自己模拟成 USB Device，让电脑识别成虚拟串口，依赖：

```text
CONFIG_USB_GADGET
CONFIG_USB_CONFIGFS
CONFIG_USB_CONFIGFS_ACM
```

Host 与 Device 属于不同方向、不同子系统，后续裁剪时禁止混淆。

### USB 控制器与物理接口拓扑

状态：`[VERIFIED TOPOLOGY]`

配套图解见：[06 - RK3568 GEC V11 USB 图解](06_usb_visual_guide.md)。

本节结论来自 GEC V11 原理图、RK3568 EVB 资料、运行时控制器状态及实际 USB 插拔测试。Rockchip 节点名中的 `host` / `otg` 不能直接当作板上接口名称，必须结合控制器地址和实际走线判断。

| PHY 节点 | 实际功能 | 控制器 / 下游 | GEC V11 接口 | 当前结论 |
|----------|----------|---------------|--------------|----------|
| `u2phy0_otg` | USB3 OTG0 的 USB2 PHY | `fcc00000` DWC3 | J604 OTG | `[VERIFIED KEEP]` |
| `u2phy0_host` | USB3 HOST1 的 USB2 PHY | xHCI | J600 USB3 Type-A | `[VERIFIED KEEP]` |
| `u2phy1_otg` | USB2 HOST2 | `fd800000` EHCI + `fd840000` OHCI -> U601 HUB | J601 / J602 / J603 | `[VERIFIED KEEP]` |
| `u2phy1_host` | USB2 HOST3 | `fd880000` EHCI + `fd8c0000` OHCI | GEC V11 未使用 | `[VERIFIED DISABLED]` |

关键反证实验：关闭 `u2phy1_otg` 后，J601/J602/J603 仍有 5 V，但 USB 数据设备完全无法枚举。因此 `u2phy1_otg` 实际服务板载 U601 HUB，不能因为节点名带 `otg` 就删除。

对 HOST3 动态解绑 `fd880000` / `fd8c0000` 后，Bus 5 / Bus 6 消失，但 U601 HUB 三个 USB2 口、USB3 Host 和 OTG 均保持正常。该结果支持在 GEC V11 上关闭 `u2phy1_host`、`usb_host1_ehci` 和 `usb_host1_ohci`。

当前推荐状态：

```dts
&u2phy0_host {
    phy-supply = <&vcc5v0_host>;
    status = "okay";
};

&u2phy0_otg {
    vbus-supply = <&vcc5v0_otg>;
    status = "okay";
};

&u2phy1_otg {
    phy-supply = <&vcc5v0_host>;
    status = "okay";
};

&u2phy1_host {
    phy-supply = <&vcc5v0_host>;
    status = "disabled";
};

&usb_host0_ehci {
    status = "okay";
};

&usb_host0_ohci {
    status = "okay";
};

&usb_host1_ehci {
    status = "disabled";
};

&usb_host1_ohci {
    status = "disabled";
};
```

上述片段是当前已验证状态的记录，不代表本轮修改了 SDK 中的 DTS。

### USB 端口实测

状态：`[VERIFIED]`

正常运行时已确认存在以下设备链路：

```text
xHCI USB2 root hub
xHCI USB3 root hub
fd800000 EHCI root hub
fd840000 OHCI root hub
1a40:0101 USB2.0 HUB
```

U601 工作在 `480 Mbps High-Speed`。外接 CH340（`1a86:7523`）已经分别在 U601 三个下游口枚举为：

```text
3-1.1
3-1.2
3-1.3
```

并成功出现：

```text
ch341-uart converter detected
ch341-uart converter now attached to ttyUSB0
```

这证明 U601 HUB 及三个下游 USB2 数据口均可用，也证明当前开发环境保留 `CONFIG_USB_SERIAL_CH341` 能支持外接 CH340。它不改变“板载调试 CH340 由 PC 端加载驱动”的结论。若产品最终不需要 RK3568 USB Host 支持外接 USB 转串口，仍可在后续独立实验中评估裁剪 `CONFIG_USB_SERIAL*`。

### Bluetooth

状态：`[HCI + FIRMWARE VERIFIED / RF AND PAIRING PENDING]`

板载无线芯片为 RTL8723DS，Bluetooth 通过 UART8/H5 而不是 Wi-Fi 使用的 SDIO。当前已验证：

```text
Rockchip RFKill state 0 -> 1
rtk_hciattach /dev/ttyS8 rtk_h5
IC: RTL8723DS
Load FW rtlbt/rtl8723d_fw OK, size 54980
Final speed 1500000
Device setup complete
/sys/class/bluetooth/hci0
```

当前基线保留：

```text
CONFIG_BT=y
CONFIG_BT_HCIUART=y
CONFIG_BT_HCIUART_3WIRE=y
CONFIG_BT_HCIUART_RTL=y
CONFIG_RFKILL=y
CONFIG_RFKILL_RK=y
```

当前成功路径使用用户空间 `rtk_hciattach`、H5/Three-wire 和 Rockchip `bluetooth-platdata`。虽然 `CONFIG_BT_HCIUART_RTL=y` 已存在于成功配置，但它对这条用户态 attach 路径是否为最小必需项尚未做 A/B 裁剪，不在本轮删除。

`hci0` 已注册并有 BD Address，但现有输出仍为 `DOWN`，没有 `UP RUNNING`、`hcitool scan`、配对或 profile 数据。因此不能写成完整 Bluetooth 功能通过。其它蓝牙厂商或虚拟驱动，例如 `CONFIG_BT_HCIBTUSB`、`CONFIG_BT_HCIUART_ATH3K`、`CONFIG_BT_HCIBFUSB`、`CONFIG_BT_HCIVHCI`、`CONFIG_BT_MRVL`、`CONFIG_BT_MRVL_SDIO`，继续列为候选，后续每轮只裁一个功能组并回归 UART8 attach。详见 [RTL8723DS Bluetooth / UART8](09_bluetooth_rtl8723ds_uart8_2026-08-29.md)。

### Wi-Fi

状态：`[RTW88 DRIVER + FIRMWARE VERIFIED / NETWORK FUNCTION PENDING]`

DTS 与运行时确认：

```text
wifi_chip_type = rtl8723ds
SDIO device = mmc2:0001:1
Firmware version 48.0.0, H2C version 0
```

当前采用 6.1 内核自带 rtw88 模块方案，维护配置为：

```text
CONFIG_RTW88=m
CONFIG_RTW88_8723DS=m
CONFIG_RTW88_DEBUG=y
CONFIG_RTW88_DEBUGFS=y
```

已编译并按顺序加载 `rtw88_core.ko`、`rtw88_sdio.ko`、`rtw88_8723x.ko`、`rtw88_8723d.ko`、`rtw88_8723ds.ko`，固件为 `/lib/firmware/rtw88/rtw8723d_fw.bin`。这证明 SDIO 匹配、模块依赖、固件读取和芯片握手成立，但尚无 AP 扫描、关联、DHCP 与 ping 证据。

不要把 AP6XXX 与 RTL8723DS 的依赖混为一谈，也不要把旧 vendor `8723ds.ko` 与当前 `rtw88_8723ds.ko` 混为一谈。BusyBox `modprobe` 自动依赖加载仍是 `[OPEN]`；首次验证继续按依赖顺序手工 `insmod`。详细步骤见 [Wi-Fi RTL8723DS / rtw88](07_wifi_rtl8723ds_rtw88_2026-08-29.md)。

### CAN

状态：`[CAN CONTROLLER VERIFIED / PHYSICAL BUS PENDING]`

BSP 6.1 的 RK3568 节点使用：

```text
compatible = rockchip,rk3568-can-2.0
driver = rockchip_canfd.c
CONFIG_CANFD_ROCKCHIP=y
```

5.10 的 `CONFIG_CAN_RK3568` 在当前 6.1 Kconfig 中不存在；仅保留 `CONFIG_CAN=y` 只能注册 CAN 协议栈，不能让硬件控制器 probe。当前 GEC DTS 启用 `&can1`、使用 `can1m0_pins`，并将 `CLK_CAN1` 设为 200 MHz。板端已出现 SocketCAN `can0`，可配置 500 kbit/s，`ip -details` 显示 `rockchip_canfd`、`ERROR-ACTIVE`、error counter 为 0 和 `clock 200000000`。

当前必须保留：

```text
CONFIG_CAN=y
CONFIG_CAN_RAW=y
CONFIG_CAN_DEV=y
CONFIG_CAN_CALC_BITTIMING=y
CONFIG_CANFD_ROCKCHIP=y
```

`CONFIG_CAN_BCM` 与 `CONFIG_CAN_GW` 是否属于最终产品需求可后续单独裁剪，但不能在 CAN 基础收发验证前混入本轮。内部 loopback、板载收发器和双节点物理总线仍是 `[PENDING]`。详细证据见 [RK3568 CAN1 控制器修复与验证](08_can_rk3568_2026-08-29.md)。

### Touch

状态：`[KEEP GOODIX / PROBE VERIFIED / FUNCTION PENDING]`

GEC V11 实际使用 Goodix 触摸屏，必须保留：

```text
CONFIG_TOUCHSCREEN_GOODIX=y
```

早期启动日志曾出现：

```text
Goodix-TS 1-005d: supply AVDD28 not found, using dummy regulator
Goodix-TS 1-005d: supply VDDIO not found, using dummy regulator
Error reading from 0x8140
I2C communication failure: -6
```

Linux 6.1.99 #22 已取得新证据：

```text
Goodix-TS 1-005d: ID 911, version: 1060
Goodix-TS 1-005d: No touchscreen properties in eeprom, using defaults
input: Goodix Capacitive TouchScreen as .../input/input3
```

因此旧的 I2C probe 失败已不再是当前状态。驱动必须继续保留，下一步改为验证 `/dev/input/eventX` 是否持续产生正确坐标/中断，并根据原理图补 AVDD28/VDDIO supply；`goodix_911_cfg.bin` 只有在板上默认配置不能满足触摸范围、方向或时序时才需要加入 rootfs。

开发阶段建议暂保留：

```text
CONFIG_HID_MULTITOUCH
```

其他触摸或鼠标驱动如 `CONFIG_TOUCHSCREEN_ATMEL_MXT`、`CONFIG_TOUCHSCREEN_GSL3673`、`CONFIG_TOUCHSCREEN_GT1X`、`CONFIG_TOUCHSCREEN_ELAN`、`CONFIG_TOUCHSCREEN_USB_COMPOSITE`、`CONFIG_MOUSE_CYAPA`、`CONFIG_MOUSE_ELAN_I2C` 可作为后续裁剪候选。

### PMIC / regulator

状态：`[VERIFIED KEEP]`

实际 PMIC 为 RK809，但 Linux 驱动命名中大量复用 RK808/RK809/RK817：

```text
CONFIG_MFD_RK808=y
CONFIG_REGULATOR_RK808=y
```

这些不能因为名称是 RK808 就删除。

已确认存在 FAN53555：

```text
CONFIG_REGULATOR_FAN53555=y
```

其他 regulator 如 RK806、ACT8865、LP8752、MP8865、RK860X、TPS65132、TPS6586X、XZ3216 等，必须结合 DTS / 原理图判断后再删。

### Battery / Charger

状态：`[CANDIDATE IF NO BATTERY]`

如果最终确认板子没有电池充放电功能，可以考虑删除 `CONFIG_BATTERY_*` 和 `CONFIG_CHARGER_*`，例如：

```text
CONFIG_BATTERY_RK817
CONFIG_CHARGER_RK817
```

但不能因为没有电池，就删除 RK809 PMIC 主体或 regulator。

### GPU

状态：`[VERIFIED KEEP]`

RK3568 GPU 是 Mali-G52，属于 Bifrost。日志已确认 `mali0` 正常 probe，必须保留：

```text
CONFIG_MALI_BIFROST=y
```

旧 Mali Midgard / Mali400 等通用配置可作为候选，但不能删除 Bifrost。

### NPU

状态：`[KEEP WHILE PRODUCT NEEDS RKNN]`

当前存在：

```text
CONFIG_ROCKCHIP_RKNPU=y
```

日志中出现过 `can't request region`、`IRQ npu_irq not found` 等 warning，但驱动最终仍初始化。若产品需要 RKNN / NPU，不能仅凭 warning 删除 RKNPU。是否可删必须以真实 RKNN workload 验证为准。

### regulator_summary / DVS 判断

状态：`[RULE]`

![GEC V11 简化供电树](../../assets/power/gec-v11-regulator-tree.png)

上图把 DTS 父子供电关系与 `regulator_summary` 中的运行时框架记录放在一起理解；它用于梳理电源树，不代表已经用万用表测得每一路实际电压。

不要仅根据 `regulator_summary` 中的 `vdd_cpu`、`vdd_gpu`、`vdd_npu` 电压值直接判断“电压过高”“DVFS 失效”或“PMIC 发热根因已确认”。

判断电压是否正常需要同时看：

```text
当前频率
OPP 表
governor
bin
leakage
pvtm
AVS
power domain
clock state
```

`there is no dvs0 gpio` / `there is no dvs1 gpio` 也不能直接推导 FAN53555 无法动态调压。FAN53555 可通过 I2C VSEL 寄存器调压。怀疑 DVFS 时，先验证 `scaling_cur_freq` 与 `regulator_summary` 中 `vdd_cpu` 是否随负载变化，不要先改 OPP。

## 当前待确认候选

| 功能组 | 候选配置 / 方向 | 初步风险 | 当前判断 |
|--------|------------------|----------|----------|
| HDMI RX | `CONFIG_VIDEO_ROCKCHIP_HDMIRX` | 低到中 | 若无 HDMI 输入采集硬件，可删 |
| RK628 / 视频桥 | `CONFIG_RK628_MISC*`、`CONFIG_VIDEO_LT6911*`、`CONFIG_VIDEO_LT7911D`、`CONFIG_VIDEO_TC35874X`、`CONFIG_VIDEO_RK628_*` | 低到中 | 裁剪前先查 DTS 是否有节点 |
| USB Serial Host | `CONFIG_USB_SERIAL*` | 中 | 开发阶段已用外接 CH340 验证，当前保留；量产最小配置是否删除需另做实验 |
| 其他 Bluetooth vendor | 非 RTL8723DS 相关 BT 驱动 | 低到中 | 需单独蓝牙验证 |
| 其他 touchscreen | 非 Goodix / 非开发必需 HID 触摸 | 低到中 | Goodix 不可删，其他需按 DTS 判断 |
| RK808 RTC | `CONFIG_RTC_DRV_RK808` | 中到高 | 若希望 PCF8563 做主 RTC，需单轮验证 |
| Battery / Charger | `CONFIG_BATTERY_*`、`CONFIG_CHARGER_*` | 中 | 无电池时可考虑，不能影响 PMIC |
| camera | sensor / bridge / ISP 相关 | 中 | 需按实际摄像头硬件与 DTS 判断 |
| filesystem | XFS、ISO9660、NTFS、JFFS2、UBIFS、SQUASHFS、NFS 等 | 中 | 开发阶段先保留，产品阶段再定 |
| debug | PM / devres / dynamic debug / ftrace 等 | 中到高 | 最后一批裁剪 |
| DRM / VOP / fbdev | 显示核心链路 | 高 | 刚调通，暂不激进裁剪 |
| GPU / NPU / IOMMU / DMA | 图形与推理核心 | 高 | 需要 workload 级验证 |

## 已验证可删除项

| 项 | 状态 | 证据 |
|----|------|------|
| 其他 Rockchip SoC selector | `[VERIFIED REMOVED]` | RK3568 单板运行，CPU0-CPU3 共 4 核正常 |
| `CONFIG_NR_CPUS=8` 改为 `CONFIG_NR_CPUS=4` | `[VERIFIED SHRUNK]` | RK3568 为 4 核，运行时 4 核全部正常 |
| 部分无关 Audio codec | `[VERIFIED REMOVED]` | 删除后 HDMI Audio 与 RK809 codec 仍正常注册 |
| 部分无关 SoC 音频配置 | `[VERIFIED REMOVED]` | 删除后 ALSA card 结构保持正常 |
| GEC V11 未使用的 USB2 HOST3 | `[VERIFIED DISABLED]` | 动态解绑 `fd880000` / `fd8c0000` 后，U601 HUB、三个 USB2 口、USB3 Host 与 OTG 均正常 |

后续每次新增可删除项，必须补齐删除日期、删除原因、重新编译结果、启动结果、功能验证结果。

## 当前 USB 最终拓扑

```text
RK3568
├── USB3 OTG0
│   └── u2phy0_otg -> fcc00000 DWC3 -> J604 OTG       [KEEP]
├── USB3 HOST1
│   └── u2phy0_host -> xHCI -> J600 USB3 Type-A       [KEEP]
├── USB2 HOST2
│   └── u2phy1_otg -> fd800000 EHCI / fd840000 OHCI
│       └── U601 USB2 HUB -> J601 / J602 / J603        [KEEP]
└── USB2 HOST3
    └── u2phy1_host -> fd880000 EHCI / fd8c0000 OHCI  [DISABLED]
```

状态：前三条链路已经通过运行时和插拔实验确认；HOST3 已通过隔离实验确认不影响 GEC V11 已用接口。

## 当前异常 / Warning 跟踪

![USB 三类问题分开排查](../../assets/usb/usb-troubleshooting-three-issues.png)

### USB `error -71`

状态：`[PENDING STABILITY TEST]`

曾观察到：

```text
device descriptor read/all, error -71
device not accepting address ..., error -71
```

Linux errno `-71` 是 `-EPROTO`，表示 USB Protocol Error。由于同一个 CH340 已在 U601 三个端口分别成功枚举并绑定 `ttyUSB0`，当前证据不足以把该错误归因于 DTS 或 PHY 拓扑。

若错误只在快速拔插或换口时偶发，优先视为接触或枚举瞬态。最小验证方法是每个物理 USB2 口各插入一次 CH340，保持静置并通过 `dmesg -w` 观察 5 到 10 分钟，记录是否出现：

```text
USB disconnect
error -71
device not accepting address
attempt power cycle
```

若静置时仍自动断开，再检查 HUB VCC、VBUS、USB2_HOST2 D+/D-、U601 12 MHz 晶振、ESD 器件、连接器、焊接和电源压降。

### `phy-fe8b0000.usb2-phy.x: illegal mode`

状态：`[PENDING SOURCE TRACE]`

当前配置已经是 `u2phy1_host = disabled`、`u2phy1_otg = okay`，且 `usb_host1_ehci` / `usb_host1_ohci` 已关闭，但启动时仍稳定出现两条 `illegal mode`。因此旧假设“两个 USB2PHY1 端口同时启用导致 illegal mode”已被后续实验否定。

`fe8b0000` 对应 USB2PHY1，当前保留的两个消费者是服务 HOST2 / U601 HUB 的：

```text
fd800000 EHCI
fd840000 OHCI
```

目前仅能标记为高概率：HCD 初始化时传入了 Rockchip USB2 PHY 驱动未接受的 `phy_mode`。下一步应在实际 6.1 源码中追踪：

```text
drivers/usb/core/hcd.c
drivers/phy/rockchip/phy-rockchip-inno-usb2.c
include/linux/phy/phy.h
PHY_MODE_USB_HOST_SS
PHY_MODE_USB_HOST
rockchip_usb2phy_set_mode()
```

必要时临时输出 `mode` / `submode` 和调用栈。获取确切参数与调用者之前，禁止为了消除日志而删除 `dev_info("illegal mode")`，也不要再次改变已验证的 PHY 拓扑。

### Type-C / OTG 反向供电

状态：`[PENDING HARDWARE MEASUREMENT]`

现象：拔掉 DC 电源后，J604 Type-C / OTG 仍连接 PC 时，板卡还能获得供电。该问题与 USB 数据 PHY 裁剪分开跟踪。

原理图链路暂记录为：

```text
J604 VBUS -> VDD_OTG -> U602 SY6280AAC -> VCC_5V
```

同时存在 DTS 与原理图标注可能不一致的风险：DTS 的 `vcc5v0_otg` 使用 `gpio0 RK_PA5`，当前原理图上 U602 EN 看起来标为 `GPIO0_C3`。在确认 PCB revision 和真实电路前不得直接改 DTS。

最小硬件实验：DC 拔掉、Type-C 接 PC，分别测量 U602 `OUT`、`EN`、`IN` 的实际电压并记录。结果出来后再判断是否存在 U602 反向供电、GPIO 标注差异或其他电源回灌路径。

## 当前推荐最终 DTS

当前仅对 USB 部分形成推荐状态，内容见“USB 控制器与物理接口拓扑”中的 DTS 片段。该状态的证据边界如下：

- `[VERIFIED]` `u2phy0_host`、`u2phy0_otg`、`u2phy1_otg` 保持启用。
- `[VERIFIED]` `u2phy1_host`、`usb_host1_ehci`、`usb_host1_ohci` 可关闭。
- `[PENDING]` 不因 `illegal mode` warning 继续调整 PHY 节点。
- `[PENDING]` 不在测量 U602 和确认 PCB revision 前修改 `vcc5v0_otg` GPIO。

本节只维护推荐状态，不表示已经自动修改 SDK 的 DTS。

## 下一步测试计划

当前只推进一个最小实验：

```text
对 J601、J602、J603 各做一次 CH340 静置稳定性测试；每个端口保持 5 到 10 分钟，使用 dmesg -w 记录是否出现 disconnect 或 error -71。
```

该实验完成前，不对 `error -71` 做 DTS / PHY 归因，也不追加新的 USB 裁剪动作。

## 裁剪日志

### 2026-08-29：定位 LVGL CAN Test 的 `Operation not supported`

状态：`[ROOT CAUSE VERIFIED / APP FIX PENDING]`

补充的 LVGL CAN 页面源码确认 `can_init()` 执行：

```text
ip link set can0 type can bitrate 500000 dbitrate 500000 fd on
```

当前 `rockchip,rk3568-can-2.0` 在 `rockchip_canfd.c` 中映射为 `ROCKCHIP_RK3568_CAN_MODE`，其 `ctrlmode_supported` 不包含 `CAN_CTRLMODE_FD`。因此 `fd on` 触发驱动返回 `-EOPNOTSUPP`，由 `ip` 打印 `RTNETLINK answers: Operation not supported`。这不是 CAN1 DTS、时钟或经典 CAN 500 kbit/s 失败；应用应删除 `dbitrate 500000 fd on`。

同一源码把 `rfilter.can_id` 设为 `-1`、mask 设为 `CAN_SFF_MASK`。`-1` 会置位 `CAN_INV_FILTER`，实际成为反向过滤，并非注释中的“只收 0x22”或“接收全部”。接收全部应使用 ID/mask 均为 0；只收标准数据帧 `0x22` 应显式配置 ID `0x22` 并 mask 标准帧、扩展帧和 RTR 标志。

当前仓库只有命令字符串备份，没有找到可编辑的 LVGL CAN C 源文件，所以只落地根因和修改方案，尚未重编应用。CAN 控制器运行状态保持已验证，物理收发与应用回归仍待完成。

后续板端已按 `can0 down -> bitrate 500000 -> can0 up` 顺序成功重配。`ip -details` 再次确认 `ERROR-ACTIVE`、实时 berr-counter tx/rx 均为 0、sample point 0.875、时钟 200 MHz 且 bus-off 为 0。此前 `Device or resource busy` 的原因是接口处于 UP 状态，并非 bit timing 不受支持。

统计中出现 RX 556155 packets / 4449240 bytes、累计 error-warn/error-pass 各 1 和 TX dropped 1，但没有帧 ID/payload；同时 `ip` 输出的 promiscuity/queue 数值明显异常。因此当前只升级为 `[CLASSIC CAN RECONFIG VERIFIED]`，仍需 sysfs 计数和 `candump` 交叉验证。

### 2026-08-29：RTL8723DS Bluetooth 完成 H5 固件下载与 hci0 注册

状态：`[BLUETOOTH HCI + FIRMWARE RUNTIME VERIFIED / RF PENDING]`

初始系统已经注册 Bluetooth core、HCI UART H4/H5、RFCOMM 与 HIDP，Rockchip `bluetooth-platdata` 也解析到 UART RTS、reset、wake 和 host-wake GPIO；但 RFKill 状态为 0，`/sys/class/bluetooth/` 为空。

板端确认 rootfs 已提供 `rtk_hciattach`、`hciattach`、`hciconfig` 和 `hcitool`，并存在 `rtlbt/rtl8723d_fw` 与 `rtl8723d_config`。手工将 Bluetooth RFKill 置 1 后执行：

```bash
rtk_hciattach -n -s 115200 /dev/ttyS8 rtk_h5 &
```

关键结果：

```text
IC: RTL8723DS
Load FW /lib/firmware/rtlbt/rtl8723d_fw OK, size 54980
FW version 0xaaa82df5, Patch num 3
Final speed 1500000
Received cc of hci reset cmd
Device setup complete
```

随后 `/sys/class/bluetooth/hci0` 出现，`hciconfig -a` 可读到 UART bus、BD Address、ACL/SCO MTU，RX/TX error 均为 0。控制器当时仍是 `DOWN`，未提供 `hciconfig hci0 up`、扫描、配对与业务 profile 输出，因此只确认 HCI 和固件链路。

UART8 同时报告缺少 DMA 属性并回退到 interrupt mode，但该模式下仍完成 H5、固件下载、1.5 Mbit/s 切速和 HCI reset。本轮不把 DMA warning 归因为功能失败，也不在未核对 DMA request 前直接补通道号。

### 2026-08-29：修复 RK3568 CAN1 驱动配置并注册 SocketCAN

状态：`[CAN CONTROLLER RUNTIME VERIFIED / PHYSICAL BUS PENDING]`

初始启动只出现 CAN core、RAW、BCM 与 gateway 日志，`ip link show` 没有 CAN 接口。源码核查确认 `rk356x.dtsi` 的 `rockchip,rk3568-can-2.0` 由 `rockchip_canfd.c` 匹配，而当时 `.config` 为 `# CONFIG_CANFD_ROCKCHIP is not set`。

修正内容：

```text
defconfig: CONFIG_CANFD_ROCKCHIP=y
DTS: &can1 使用 can1m0_pins
DTS: assigned-clocks = <&cru CLK_CAN1>
DTS: assigned-clock-rates = <200000000>
```

重新编译、烧写后，DTS label `can1` 对应的 `fe580000.can` 作为系统第一个 CAN 网络设备注册为 `can0`。板端实证：

```text
can state ERROR-ACTIVE (berr-counter tx 0 rx 0)
bitrate 500000 sample-point 0.875
rockchip_canfd
clock 200000000
```

结论：控制器驱动、时钟、pinmux、bit timing 与 SocketCAN netdev 已运行验证。尚未取得 `candump/cansend` loopback 或双节点物理总线帧，不升级为 CAN 物理链路完全通过。

### 2026-08-29：RTL8723DS 切换 rtw88 并完成固件握手

状态：`[DRIVER + FIRMWARE RUNTIME VERIFIED / WIFI FUNCTION PENDING]`

6.1 源码树中没有 5.10 使用的完整 vendor `rtl8723ds` 驱动，但内核自带 rtw88 对 RTL8723DS 提供支持。本轮将 GEC 专用 defconfig 固化为模块方案，实际 `.config` 展开为：

```text
CONFIG_RTW88=m
CONFIG_RTW88_CORE=m
CONFIG_RTW88_SDIO=m
CONFIG_RTW88_8723X=m
CONFIG_RTW88_8723D=m
CONFIG_RTW88_8723DS=m
```

五个模块的 `vermagic` 均为 `6.1.99 SMP mod_unload aarch64`，固件使用 `rtw88/rtw8723d_fw.bin`。内置 `=y` 实验中，驱动在 rootfs 挂载前 probe，因无法读取 rootfs 固件而报 `error -2`；改成模块并重新烧写对应内核后，按依赖顺序手工加载成功：

```text
rtw_8723ds mmc2:0001:1: Firmware version 48.0.0, H2C version 0
```

这条日志证明 SDIO 设备、rtw88 驱动和固件握手完成；后续同日输出已确认 `wlan0` 注册。当前仍未收到 AP 扫描、关联、DHCP 和 ping 的完整输出，因此 Wi-Fi 网络功能保持 `[PENDING]`。板端 BusyBox 缺少可靠的 `depmod`，自动加载方案也要在生成完整模块元数据或固化顺序加载脚本后重启复验。

### 2026-08-28：DTS 结构与文件归属修正

状态：`[BSP-6.1 DTS STRUCTURE VERIFIED]`

旧规则：

```text
永不修改 rk3568-evb1-*.dtsi 等 Rockchip 官方文件；只维护一个 GEC override。
```

问题：这个通配符会错误匹配 `rk3568-evb1-gec-v11.dtsi`。该文件虽采用 EVB1 风格命名，但实际是 GEC 自有板级文件；当前 6.1 也不是“一个 override + 一个薄入口”的结构。

核实结果：

```text
rk3568-evb1-gec-v11-linux.dts
├── rk3568-evb1-gec-v11.dtsi
│   ├── rk3568.dtsi
│   │   └── rk356x.dtsi
│   └── rk3568-evb-gec.dtsi
└── rk3568-linux.dtsi
```

| 文件 | 核实来源 / 差异 | 归属 |
|------|-----------------|------|
| `rk3568-evb1-gec-v11-linux.dts` | 复制自 6.1 `rk3568-evb1-ddr4-v10-linux.dts`，初始仅替换 include | GEC 可维护顶层 |
| `rk3568-evb1-gec-v11.dtsi` | 5.10 `rk3568-gec-v11.dtsi` 改名复制，核实时 diff 为 0 | GEC 可维护板级层 |
| `rk3568-evb-gec.dtsi` | 复制自 5.10 同名文件，6.1 侧已有少量差异 | GEC 可维护主内容层 |
| `rk3568.dtsi` / `rk356x.dtsi` / `rk3568-linux.dtsi` | 6.1 原生共享层 | 当前 GEC 板级适配不直接修改 |

当前编译目标：

```text
RK_KERNEL_DTS_NAME="rk3568-evb1-gec-v11-linux"
rk3568-evb1-gec-v11-linux.dtb
```

修正后的规则：按**文件来源、职责和是否带 GEC 板级内容**判断归属，不按 `rk3568-evb1-*` 前缀判断。三个带 `gec` 的当前派生文件都允许并需要继续维护；共享 SoC / Linux 基线继续复用。2026-08-24 日志中的 `rk3568-gec-v11-*` 名称作为当日证据保留，但已明确标注不是当前结构。

本次只修正文档与维护规则，不代表新增板端功能验证；DSI LCD、NPU warm-reset 等状态保持不变。

### 第 1 轮：USB 拓扑收敛与 HOST3 隔离验证

日期：2026-08-28

修改前：USB2PHY1 的 `host` / `otg` 命名与 GEC V11 物理端口对应关系不明确，HOST3 是否被板卡使用尚未形成项目内证据链。

修改内容：

```text
u2phy1_host = disabled
usb_host1_ehci = disabled
usb_host1_ohci = disabled
u2phy1_otg = okay
usb_host0_ehci = okay
usb_host0_ohci = okay
```

预期：关闭未使用的 USB2 HOST3，同时保留 U601 HUB、三个 USB2 Host 口、USB3 Host 和 OTG。

实际结果：动态解绑 HOST3 的 `fd880000` / `fd8c0000` 后 Bus 5 / Bus 6 消失，其余 USB 链路正常；U601 三个下游口均可识别同一外接 CH340 并绑定 `ttyUSB0`。

关键日志：

```text
1a86:7523
ch341-uart converter detected
ch341-uart converter now attached to ttyUSB0
```

结论：`[VERIFIED]` GEC V11 未使用 USB2 HOST3，可关闭对应 PHY 端口与 EHCI/OHCI；`u2phy1_otg` 实际服务 HOST2 / U601 HUB，必须保留。

是否可进入最终配置：是。当前记录表明该状态已经过板端隔离和插拔实验，但未经用户明确确认时不自动提交 Git。

影响范围：USB2 HOST3（EVB 独立接口）不可用；GEC V11 已用 USB 接口不受影响。

回滚方式：将 `u2phy1_host`、`usb_host1_ehci`、`usb_host1_ohci` 恢复为 `status = "okay"`，重新编译并烧录 DTB / boot.img。

### 第 0 轮：建立长期裁剪纪律与基线

日期：2026-08-28

内核版本：Rockchip vendor Linux 6.1.x

目标：把 GEC RK3568 DDR4 V11 Linux 6.1 的裁剪规则、已验证硬件结论、保留项、候选项和日志模板落地到项目文档。

修改前：

```text
6.1 裁剪规则主要散落在对话、启动日志分析和零散笔记中。
```

修改后：

```text
docs/porting/rockchip-6.1/05_kernel_trim_validation_log.md
```

修改依据：

- 项目当前 BoardConfig 已切到 `rockchip_rk3568_gec_linux_defconfig`
- 6.1 已完成 CPU selector / NR_CPUS 初步裁剪
- `CONFIG_FB=y` 已验证解决 `/dev/fb0` 缺失
- HDMI、ALSA、UART、RTC、GPU、部分 NPU 初始化已有运行时证据
- CH340、USB Serial Host、USB Gadget Serial 的方向已明确

重新生成 `.config`：本轮未修改内核配置，不适用。

编译：本轮未修改内核源码，不适用。

烧录：本轮未修改镜像，不适用。

启动：本轮基于既有启动日志整理，不新增板端启动。

功能验证：

| 功能 | 当前结论 |
|------|----------|
| CPU | 已验证 RK3568 / 4 核 |
| Display | `CONFIG_FB=y` 后 fb0 已验证 |
| HDMI | 1920x1080@60 已验证 |
| DSI | 暂未完成本轮实机复测 |
| Audio | HDMI Audio + RK809 codec 已验证 |
| Ethernet | 本文件未新增结论 |
| Wi-Fi | RTL8723DS 的 rtw88 模块与 firmware 握手已验证；扫描、关联、DHCP、ping 待验证 |
| Bluetooth | RTL8723DS UART8/H5、固件下载和 `hci0` 注册已验证；扫描、配对与 profile 待验证 |
| USB | Host / Gadget / CH340 规则已落地 |
| RTC | RK809 RTC + PCF8563 已确认，主 RTC 选择待研究 |
| Touch | Goodix 已读出 GT911 ID 并注册 input device；触摸事件实测与 supply/cfg warning 待处理 |
| CAN | CAN1 控制器、SocketCAN `can0`、500 kbit/s 与 200 MHz 时钟已验证；物理收发待验证 |
| GPU | Mali Bifrost 已确认保留 |
| NPU | RKNPU 暂保留，需 RKNN workload 验证 |

结果：`[BASELINE LOG CREATED]`

备注：后续每轮裁剪都应追加在本节后面。如果新证据推翻旧结论，必须按“旧结论 / 新证据 / 修正后的结论”格式记录。

### 2026-08-29：Linux 6.1.99 #22 完整启动日志审计

状态：`[BOOT SUCCESS / ISSUE AUDIT RECORDED]`

原始 690 行串口日志已完整保存为纯文本 `.log`，分析结论单独保存在 Markdown 文档中：

```text
logs/rockchip-6.1/boot/kernel_boot_2026-08-29_kernel-6.1.99-22.log
```

统一关键字初筛命中 62 行；合并重复与 fallback 后归并为 24 个问题族，其中 P0 致命问题 0 项、P1 功能闭环 5 项、P2 配置完整性 8 项、P3 可选/清理 11 项。系统已进入 init，eMMC/rootfs、千兆网、DRM/fb0、GPU、NPU 驱动注册、CAN 和 Bluetooth attach 均有后续成功证据。

本轮状态修正：Goodix 已不再是旧日志中的 I2C probe 失败。#22 日志读出 `ID 911, version: 1060` 并注册 `Goodix Capacitive TouchScreen`；当前边界改为“probe 通过，触摸事件、供电属性和 cfg firmware 待验证”。

本轮没有修改 defconfig、DTS、rootfs 或镜像。完整问题表、处理顺序和验收命令见 [Linux 6.1.99 #22 启动日志问题审计](10_boot_log_issue_audit_2026-08-29.md)。

### 2026-08-29：GPIO3_A4 / 4G5G regulator 极性冲突解决

状态：`[VERIFIED RESOLVED]`

原理图确认 GPIO3_A4 直接连接 U400 MP2315 的高有效 EN，控制 J400 MINI_PCIE 52PIN 的 `4G5G_3V6` 电源。6.1 GEC DTS 已将：

```dts
gpio = <&gpio3 RK_PA4 GPIO_ACTIVE_LOW>;
```

修正为：

```dts
gpio = <&gpio3 RK_PA4 GPIO_ACTIVE_HIGH>;
```

编译 DTB 反编译结果的 GPIO flag 为 `0x00`，证明修改已进入镜像。板端新镜像启动后，连续三次执行以下命令均无输出：

```shell
dmesg | grep -F 'GPIO handle specifies active low - ignored'
```

因此 #22 审计中的 24 个问题族已有 1 项关闭，当前剩余 23 项未闭环。该结论仅表示极性冲突与 warning 已解决，不代表 `4G5G_3V6` 实测电压或 4G/5G 模块枚举已经通过。原始证据见 `logs/rockchip-6.1/power/pcie_4g5g_regulator_polarity_2026-08-29.md`。

## 后续追加模板

```text
【第 X 轮裁剪】

日期：
内核版本：

目标：

修改前：

修改后：

修改依据：
- DTS：
- 启动日志：
- /proc：
- /sys：
- 实际硬件：
- 其他：

重新生成 .config：
通过 / 不通过

编译：
通过 / 不通过

烧录：
通过 / 不通过

启动：
正常 / 异常

功能验证：
CPU：
Display：
HDMI：
DSI：
Audio：
Ethernet：
Wi-Fi：
Bluetooth：
USB：
RTC：
Touch：
CAN：
GPU：
NPU：
其他：

结果：
裁剪成功 / 暂时保留 / 回退

备注：
```

## 当前裁剪进度

已验证成功：

- RK3568 SoC selector 收敛，只保留 `CONFIG_CPU_RK3568=y`
- `CONFIG_NR_CPUS=4`
- UART 数量收敛到 10，已见 `ttyS0` / `ttyS1` / `ttyS4` / `ttyS8`
- `CONFIG_FB=y` 补齐后 `/dev/fb0` 创建成功
- HDMI 1920x1080@60 输出成功
- HDMI Audio + RK809 codec 注册成功
- PCF8563 驱动与设备存在，alarm 异常已清理
- Mali Bifrost probe 成功
- RK3568 CAN1 由 `rockchip_canfd` 注册为 `can0`，500 kbit/s 与 200 MHz 时钟已验证

当前待处理：

- DSI LCD 实机复测
- LVGL 1024x600 与 HDMI 1920x1080 framebuffer 尺寸不匹配
- Goodix 使用 `evtest` 验证触摸事件、坐标和中断，再按原理图补 supply / 可选 cfg firmware
- Wi-Fi RTL8723DS 补齐 AP 扫描、关联、DHCP、网关与外网 ping 证据
- rtw88 模块自动加载方案生成完整依赖元数据或固化顺序加载后，做冷启动复验
- CAN 使用 `can-utils` 完成内部 loopback，并用两个节点验证物理总线双向收发
- 找到 LVGL CAN 页面实际 C 源文件，删除 `fd on/dbitrate`、修正 CAN_RAW filter 后重编并回归测试
- Bluetooth 将 `hci0` 置为 `UP RUNNING`，完成 inquiry 扫描、配对和目标 profile 验证
- 固化 Bluetooth RFKill + `rtk_hciattach` 自动启动后做冷启动复验
- RTC 主设备从 RK809 切到 PCF8563 的可行性验证
- HDMI RX / RK628 / 视频桥裁剪
- 三个 USB2 口逐口进行 CH340 静置稳定性测试，确认 `error -71` 是否只在快速拔插时出现
- 追踪 USB2PHY1 `illegal mode` 的实际 `mode` / `submode` 与调用者
- 测量 Type-C 接 PC、DC 断开时 U602 `IN` / `OUT` / `EN`，排查反向供电
- USB Serial Host 在开发配置中暂保留；量产最小配置是否保留常见 USB-UART 兼容能力待定
- 文件系统与 debug 配置后期收敛
