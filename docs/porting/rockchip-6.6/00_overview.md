# RK3568 EVB1 → 主线内核（Linux 7.x / 6.18 LTS）移植评估

> 目标：把粤嵌（Yueqian）RK3568 开发板的出厂 Buildroot 系统（内核 4.19.232）迁移到
> **基于 Linux 7.x 或 6.18 LTS 主线内核的 Buildroot**，用于学习 Linux 系统与构建流程。
> 本文汇总 DTS 逆向分析、屏幕原理图核对、屏幕驱动难点（T2）来龙去脉，以及落地路线。
> 配套代码见同目录：`panel-himax-evb1.c`、`rk3568-evb1-v10-panel.dts`。

> 🔀 **方向变更（2026-08-08）**：原目标「主线 6.18」已调整为 **Rockchip BSP 6.6**（`linux-rockchip` `stable-6.6` 分支）。
> 原因：主线任意版本（6.6 / 6.18 / 7.x）均无 RK3568 NPU 官方驱动（主线 "Rocket" 驱动仅 RK3588+），而项目需要 NPU。
> BSP 6.6 含 **in-tree `rknpu`**、`rkvdec`/`mpp`/`isp`，且厂内 `panel-simple` 补丁会解析 `panel-init-sequence` → MIPI-DSI 屏**靠改 DTS 即点亮**（原 T2 自定义驱动 `panel-himax-evb1.c` 不再必需）。
> **本文以下分析仍有效**（DTS 交叉核对、init 序列、WiFi 方案），但「内核基底」一律按 BSP 6.6 理解；NPU 从 T3 放弃改为「BSP 自带，可用 rknn-toolkit2 跑推理」。
> 最新进展见 `docs/porting/mainline-6.18/10_debug_notes.md`（续8 起）。

---

## 1. 一句话结论

**整体难度：中等偏低，对个人学习项目很可行。** 板子本质是 Rockchip 官方 EVB 原版（粤嵌未改设备树），
内核基底改为 **Rockchip BSP 6.6**（LTS，含 in-tree `rknpu` / `rkvdec` / `mpp` / `isp`），核心系统改动极小；
原评估里最难的 **T2 屏驱动已被 BSP 自带 `panel-simple` 补丁化解**——MIPI-DSI 屏靠改 DTS（`panel-init-sequence`）即点亮，无需自写驱动。
建议**保留厂商 U-Boot，只换 kernel + dtb**。

---

## 2. 板子本质：Rockchip 官方 EVB，不是野板

从出厂 `boot.img` 提取 dtb 反编译得到的 `hardware/Device Tree/rk3568.dts`：

```
compatible = "rockchip,rk3568-evb1-ddr4-v10", "rockchip,rk3568";
model      = "Rockchip RK3568 EVB1 DDR4 V10 Board";
```

→ 这就是 Rockchip 官方 EVB1 DDR4 V10 的**原版设备树**，粤嵌零改动。
主线 `arch/arm64/boot/dts/rockchip/` 下已有：

```
rk356x-base.dtsi   (1989 行，SoC 级 IP)
rk3568.dtsi        (416 行，RK3568 特有)
rk3568-evb1-v10.dts (751 行，板级）
```

这意味着：起步不需要从零写设备树，而是在主线 `rk3568-evb1-v10.dts` 基础上**局部增改**。

### 统计
- 286 个带 `compatible` 的节点，219 启用 / 67 disabled。
- 主线 `rk356x-base.dtsi` 已覆盖：cru/pmucru/pinctrl/grf、uart、i2c、pwm、spi、sfc、dw-mshc、
  dwcmshc(eMMC)、gmac、usb2phy/dwc3/ehci/ohci、combphy、pcie、dwc-ahci、tsadc、saradc、wdt、
  i2s-tdm、spdif、pdm、**mali(Panfrost)**、iommu、vop(VOP2)、dw-hdmi、mipi-dsi、dsi-dphy、csi-dphy、
  **rga / vpu / vepu / vicap**、qos、otp、rng、dfi。

---

## 3. 关键发现：屏幕是 MIPI-DSI，不是 LVDS

`README.md` 旧版写"HDMI 2.0 + LVDS"，**这是错的**。三重证据：

1. DTS 里 `lvds` / `rgb` / `edp@fe0c0000` 全部 `status = disabled`；`dsi@fe060000` 启用。
2. 启用的 DSI 面板：`simple-panel-dsi`，**1024×600@60，4 lane，像素时钟 51.2 MHz**，
   hfp160 / hsync2 / hbp160 / vfp12 / vsync2 / vbp23。
3. 出厂启动日志佐证：`dw-mipi-dsi fe060000.dsi` + `VOP update mode to: 1024x600p60, type: MIPI0 for VP0`。

> ⚠️ 原理图丝印把屏幕接口也标成 "LCD/MIPI"，底板 J500/J501 即 MIPI_DSI 4 lane。LVDS 在 DTS 中从未启用。

---

## 4. 屏幕原理图 ↔ DTS 交叉核对（已用 PyMuPDF 提取 PDF 文本核对）

| 信号 | 原理图（底板 V10 / 屏幕转接板） | DTS 反编译 | 结论 |
|------|------|------|------|
| 屏接口 | J500/J501 = MIPI_DSI 4 lane | `dsi@fe060000` enabled, 4 lane | ✅ MIPI-DSI |
| 触摸 I2C | I2C1_SDA/SCL_TP | `gt911@5d` on `i2c@fe5a0000`(i2c1) | ✅ |
| 触摸中断 | GPIO3_B3 / TP_INT | `irq-gpios=<0x41 0x0b>` (gpio3 B3) | ✅ |
| 触摸复位 | GPIO3_B4 / TP_RST | `reset-gpios=<0x41 0x0c>` (gpio3 B4) | ✅ |
| 面板复位 | GPIO3_A7 / LRSTB | `reset-gpios=<0x41 0x07>` (gpio3 A7) | ✅ |
| LCD 使能 | GPIO0_C7 (vcc3v3-lcd0-n) | `gpio=<0x37 0x17>` (gpio0 C7) | ✅ |
| 背光 PWM | 丝印 LCD_BL_PWM4 | `pwms=<0x135>` → `pwm@fe6e0010` = **pwm5** | ⚠️ 见 §6 |

> ⚠️ **背光 PWM 索引坑**：原理图标 "PWM4"，但 DTS 实测用 `fe6e0010` = 内核 `pwm5`；
> 而主线 `rk3568-evb1-v10.dts` 用 `&pwm4`。移植到主线时该索引要 **+1** 对齐（或沿用厂商 pwm5 值）。
> 以 DTS 为准——原理图只是丝印编号口径不一致。

---

## 5. T2 硬骨头：MIPI-DSI 屏驱动的来龙去脉

### 5.1 面板 IC 是 Himax 系，但密码非主线

把 DTS 的 `panel-init-sequence` 机器解析（DSI 面板那段）得到 **20 条命令**，开头两段：

```
[00] 0x11                 ; DCS exit sleep (delay 250 ms)
[01] 0xb9 0xf1 0x12 0x83  ; SETEXTC 厂商扩展命令解锁，密码 F1 12 83
[02] 0xba 0x33 0x81 ...   ; Himax 私有寄存器序列（28 字节）
...
[19] 0x29                 ; DCS display on (delay 50 ms)
```

`B9` 是 Himax/汇顶类 IC 的 SETEXTC（进入厂商扩展命令）解锁指令。但比对主线现有驱动：

| 主线驱动 | SETEXTC 密码 |
|---------|-------------|
| `panel-himax-hx8394.c` | `FF 83 94` |
| `panel-himax-hx83102.c` | `83 10 21` |
| `panel-himax-hx83112a.c` | `83 11 2a` |
| `panel-himax-hx8279.c` | （其它） |

**无一匹配 `F1 12 83`** → 这是一颗定制/非公版 Himax，主线没有现成驱动可"改 compatible 即用"。

### 5.2 更隐蔽的坑：`panel-init-sequence` 是 Rockchip 下游私有属性

厂商能"只改 DTS 就点亮屏"，是因为 Rockchip BSP 给 `panel-simple` 打了补丁，
让它解析 DTS 里的 `panel-init-sequence` / `panel-exit-sequence` 私有属性，自动发送这些 DCS 字节。

**主线 `panel-simple` 不解析这些属性。** 因此换主线内核时，不能把厂商 DTS 那段序列丢给
`panel-simple` 就指望屏亮——主线的 `panel-simple` 会直接忽略它。

### 5.3 正确做法（已给出骨架）

把 20 条命令**原样搬进一个真实的 `drm_panel` 驱动**的 `prepare()`，用
`mipi_dsi_dcs_write_seq()` 发送。好消息：**命令本身已完整，搬过去即可，无需从零逆向寄存器**。

本仓库已生成可直接合入主线的骨架：

- `docs/porting/panel-himax-evb1.c`
  - `compatible = "gec,rk3568-evb1-dsi-panel"`（需与 DTS 一致）
  - `prepare()` 完整重放 20 条 init 命令（字节级从 DTS 生成，杜绝手抄错误）
  - 复位/使能 GPIO、regulator、背光按 DTS 接线处理
  - 退出序列：display off (0x28) + sleep in (0x10)
  - 显示模式：1024×600@60，4 lane，RGB888，video burst
- `docs/porting/rk3568-evb1-v10-panel.dts`
  - 如何把 panel 节点接到 `&dsi0`，含 `pwm5` 背光修正提示

> 落地步骤（T2 的 2~5 天主要花在这）：
> 1. 把 `.c` 放进 `drivers/gpu/drm/panel/`，加 `Makefile` / `Kconfig` 项（已注释在文件头）。
> 2. 把 `.dts` 片段合并进 `rk3568-evb1-v10.dts`，把 `&backlight` 的 `pwm4` 改成 `pwm5`。
> 3. 编译 `CONFIG_DRM_PANEL_HIMAX_GEC_EVB1=y/m`，烧写验证亮屏。
> 4. 若图像偏移/颜色异常：微调 `bus_flags`（DTS 里 `pixelclk-active=0`、`de-active=0`）与 reset 时序。

---

## 6. 触摸 GT911（属 T1，半天级）

- 厂商 DTS：`goodix,gt911 @0x5d` on `i2c1`(`fe5a0000`)，irq `GPIO3_B3`，rst `GPIO3_B4`。
- 主线 `rk3568-evb1-v10.dts` 写的是 `goodix,gt1151 @0x14`（不同型号/地址/GPIO）。
- 改动：改 `compatible` + `reg` + `interrupts/irq-gpios/reset-gpios` 即可。
  `drivers/input/touchscreen/goodix.c` 原生支持 GT911，无需新驱动。

---

## 7. 难度分级（T0–T3）

| 层级 | 内容 | 工作量 |
|------|------|------|
| **T0 零改动** | SoC 级 IP：UART / eMMC / 千兆网 / USB / HDMI / I2C / SPI / PWM / VOP2 / Mali(Panfrost) 等，主线 `rk356x-base.dtsi` 已全覆盖 | 0 |
| **T1 半天级** | 触摸 GT911（改 compatible+reg+GPIO）、BH1750 / MPU6050 / 24C02 / PCF8563、背光、按键、`bootargs` 改 `console=ttyS2,1500000` | 0.5~1 天 |
| **T1.5 WiFi** | RTL8723DS（Fn-Link FG6223）需树外驱动 `lwfinger/rtl8723ds`，主线无原生支持（或先放弃 WiFi，用千兆过渡） | 0.5~1 天 |
| **T2 屏驱动** | ~~主线需自写 Himax 面板驱动（2~5 天）~~ → **BSP 6.6 路线下降至 T1**：厂内 `panel-simple` 补丁解析 `panel-init-sequence`，屏靠改 DTS 即点亮（背光 `pwm5→pwm4` 对齐仍需注意） | 2~5 天（主线）/ ~0.5 天（BSP） |
| **T2.5 NPU** | ~~主线 T3 放弃~~ → **BSP 6.6 自带 in-tree `rknpu`**，启用 DTS 节点即可，用户态用 `rknn-toolkit2` 跑推理 | 0.5~1 天（启用+验证） |

**BSP 6.6 自带（原主线缺失项，现已可用）**：`rknpu`（NPU）、`rkvdec`/`MPP`（硬解）、`rkisp`（ISP）、厂商 `panel-simple` 补丁。
**仍建议放弃（无论主线/BSP）**：内存变频(DMC) / eDP / LVDS / fiq-debugger / mxc6655xa。学习用途下这些不是必需。

---

## 8. 移植路线（建议）

### 8.1 总策略：保留 U-Boot，只换 kernel + dtb
U-Boot 负责 DDR 训练与镜像加载，与 7.x 内核不绑定。先不动 U-Boot，降低变砖风险。

### 8.2 内核版本选择
- 7.0 内核已 **EOL**（末版 7.0.14，2026-06-27），源码可用但不再维护。
- **主线任意版本（6.6 / 6.18 / 7.x）均无 RK3568 NPU 官方驱动**（主线 "Rocket" 驱动仅 RK3588+）→ 纯主线不适合本项目（需要 NPU）。
- ✅ **最终选择：Rockchip BSP 6.6**（`linux-rockchip` 仓库 `stable-6.6` 分支，LTS + in-tree `rknpu` / `rkvdec` / `mpp` / `isp` + 厂内 `panel-simple` 补丁）。比 6.1 更新且同为 LTS。

### 8.3 步骤
1. **搭交叉编译环境**（x86_64 Ubuntu 或 WSL）：`aarch64-linux-gnu-` 工具链。
2. **取 BSP 6.6 源码**：`git clone` `rockchip-linux/linux`，切到 `stable-6.6` 分支（非 torvalds 主线）。
3. **设备树**：以 `rk3568-evb1-v10.dts` 为基底，按 §4/§6 增改（触摸改 GT911；屏直接用厂内 `panel-init-sequence` 无需 §5.3 自写驱动；NPU 节点 BSP 已含，启用即可）。
4. **defconfig**：Buildroot 上游**没有** rk3568 defconfig（最近的是 `rock5b`/RK3588、`rock4se`/RK3399），
   拿 `rock5b_defconfig` 当模板改（选 `aarch64`、`rk3568`、开启 Panfrost / DSI / 相关面板）。
5. **编译**：`make -j$(nproc) Image dtbs`；必要时 `make modules`。
6. **烧写**：OTG 进 Loader 模式，用 RKDevTool 只刷 `boot`（kernel+dtb 打包）或单刷 `resource`/`boot` 分区；
   保留现有 U-Boot 与 rootfs（eMMC，PARTUUID 挂载）。
7. **启动排错**：串口 `ttyS2,1500000`；先看能否进命令行（核心系统），再调屏（T2）。
8. **Buildroot rootfs**（可选进阶）：用上面 defconfig 构建完整镜像替换出厂 rootfs。

### 8.4 存储分区布局（来自出厂镜像 `parameter.txt`）

RK3568 的 eMMC 分区由 `parameter.txt` 描述（单位为 512 字节扇区）。出厂有两份分区表，rootfs 的 PARTUUID 恒为 `614e0000-0000`，与 bootargs 里的 `root=PARTUUID=614e0000-0000` 完全对应。

**出厂 Buildroot（简化布局 `parameter.txt`）：**

| 分区 | 偏移 | 大小 | 说明 |
|------|------|------|------|
| `uboot` | 8 MiB | 4 MiB | 厂商 U-Boot（粤嵌 2025-08 `gecedu` 构建，`Model: Rockchip RK3568 EVB1 DDR4 V10 Board`） |
| `boot` | 12 MiB | 128 MiB | `boot:bootable`，装 FIT 镜像（`boot.img` ≈ 33 MB） |
| `rootfs` | 140 MiB | 剩余 | `rootfs:grow`，ext4，PARTUUID=`614e0000-0000` |

**更完整的 FIT 布局（`parameter-buildroot-fit.txt`）：**

`uboot(4M) / misc(4M) / boot(32M) / recovery(32M) / backup(32M) / rootfs(6G) / oem(128M) / userdata(剩)`。

**RKDevTool 烧写顺序**（`config.cfg`）：

```
loader(MiniLoaderAll.bin) → parameter → uboot → misc → boot → recovery
 → backup → oem → rootfs → userdata
```

→ 移植时**只刷 `boot` 分区**（把主线 `Image` + `rk3568-evb1-v10.dtb` 打进 FIT 替换 `boot.img`），保留 `uboot` / `misc` / `rootfs` / `userdata`，风险最低、可随时回退到出厂。

### 8.5 WiFi 模组：Fn-Link FG6223（Realtek RTL8723DS）

- 模组 datasheet：`D:\粤嵌RK3568资料-20250507\2-硬件资源\3-数据手册\Fn-Link_FG6223ASRD.pdf`，方案为 **RTL8723DS**（2.4G WiFi + BT）。
- 出厂驱动：`E:\20250526HYL\GEC-RK3568b2\4.19.219驱动\8723ds.ko`（**树外驱动，内核 4.19 专用**）。**主线没有**原生 RTL8723DS 驱动（`rtw88` 系列不支持 8723DS）。
- 主线可用方案：`lwfinger/rtl8723ds` 树外仓库，需针对 6.18 / 7.1 内核重新编译（DKMS 或随内核编为 `CONFIG_RTL8723DS=m`）。
- BT 走 UART：`rtk_hciattach /dev/ttyS8`（出厂脚本做法）。
- **结论**：WiFi 是 T1 之外的一个独立坑——要么花 0.5~1 天接树外驱动，要么先放弃 WiFi、靠千兆以太网（RTL8211F，主线 `stmmac` 原生支持，iperf 实测 **942 Mbps**）过渡。**完整板级移植方案见 §11。**

### 8.6 外围实测确认（4.19.232 启动日志 / evtest / iperf）

以下外设已在出厂系统实测可用，移植时按主线 `rk356x-base.dtsi` 默认绑定即可，基本属 T1 / 零改动：

| 外设 | 接口 | 主线驱动 | 实测备注 |
|------|------|----------|----------|
| 光照 BH1750 | i2c | `bh1750` | `iio:device2` |
| 六轴 MPU6050 | i2c | `inv_mpu6050` | `iio:device1` |
| SARADC | 片上 | `rockchip-saradc` | `iio:device0`，供 adc-keys |
| EEPROM 24C02 | i2c | `at24` | 丝印 BL24C02 |
| RTC PCF8563 | i2c | `rtc-pcf8563` | `/dev/rtc` |
| 千兆 PHY RTL8211F | RGMII | `stmmac` + `rtl821x` | iperf 实测 942 Mbps |
| 触摸 GT911 | i2c1 @0x5d | `goodix` | `event6`（见 §6） |
| 按键 | gpio / adc | `gpio-keys` / `adc-keys` | `event0` / `event3` |

> ⚠️ **资料里没有屏面板 IC 的 datasheet**（`3-数据手册` 仅有 Fn-Link / RTL8211F / BH1750 / PCF8563 / BL24C02），再次印证 T2 屏驱动只能靠已提取的 init 序列硬搬（驱动骨架 `panel-himax-evb1.c` 已就绪）。

> 📌 **一个重要事实**：这两个文件夹里**没有任何 Linux 内核源码树**——只有预编译的 `.ko` / `.img` / `boot.img` / 烧写工具。真要动手移植，主线内核得自己 `git clone` torvalds/linux（或 stable 分支）下来编，本地没有现成源码可改。

---

## 9. 已知坑清单（移植前必读）

| 坑 | 现象 | 处理 |
|----|------|------|
| README 写 "LVDS" | 误以为屏是 LVDS | 实为 MIPI-DSI（本文 §3） |
| 背光 PWM 索引 | 屏不亮但内核报 PWM 找不到 | DTS 用 `pwm5`，主线 `rk3568-evb1-v10.dts` 用 `pwm4`，改 +1 |
| `bootargs` 控制台 | 内核启动后无串口输出 | `console=ttyFIQ0` 依赖厂商 fiq-debugger；改 `console=ttyS2,1500000` |
| `panel-init-sequence` 私有属性 | 屏不亮 | 主线 `panel-simple` 不认，必须按 §5.3 写真实面板驱动 |
| WiFi 不工作 | 主线无 RTL8723DS 驱动，开机搜不到 wlan0 | 接树外 `lwfinger/rtl8723ds`，或先放弃 WiFi 用千兆（RTL8211F 主线原生） |
| Buildroot 无 rk3568 defconfig | 不知从哪起步 | 用 `rock5b_defconfig` 模板 |
| 7.0 已 EOL | 选了不再维护的内核 | 改 6.18 LTS / 7.1 stable |

---

## 10. 本目录产出文件

| 文件 | 作用 |
|------|------|
| `00_overview.md` | 本文：完整移植评估与路线 |
| `panel-himax-evb1.c` | 屏幕面板驱动骨架（init 序列从 DTS 机器生成，字节级一致） |
| `rk3568-evb1-v10-panel.dts` | 屏幕 DTS 接线片段（含 pwm5 修正） |

---

## 11. WiFi 驱动专项方案：RTL8723DS（Fn-Link FG6223）

> 本节所有引脚/GPIO 均从出厂 DTS（`hardware/Device Tree/rk3568.dts`）逐节点核对得出，非推测。
> GPIO 解码基准：phandle `0xb4 = gpio2`；RK 引脚编码 A=0..7 / B=8..15 / C=16..23 / D=24..31。

### 11.1 硬件事实（板级，已核对）

- 模组：**RTL8723DS** = WiFi(2.4G, **SDIO**) + BT(**UART**)。DTS 里 `wifi_chip_type = "rtl8723ds"` 佐证。
- **WiFi 走 SDIO，挂在 `sdmmc1`（dwmmc@fe2c0000）**：`supports-sdio` / `bus-width=4` / `non-removable` / `cap-sdio-irq` / `sd-uhs-sdr104` / `keep-power-in-suspend`，并引用 `mmc-pwrseq`（上电时序）。
- **WiFi 使能 GPIO**：`sdio-pwrseq` 的 `reset-gpios = <&gpio2 RK_PC4 GPIO_ACTIVE_LOW>`（**GPIO2_C4**，低有效，上电后延时 200ms）。
- **WiFi host-wake**：厂商属性 `WIFI,host_wake_irq = <&gpio2 RK_PC3>`（**GPIO2_C3**）——这是 Rockchip 私有属性，**主线不用**。
- **BT 走 `uart8`（serial@fe6c0000 = /dev/ttyS8）**，与启动日志 `rtk_hciattach /dev/ttyS8` 完全吻合。
- **BT 相关 GPIO**（来自厂商 `bluetooth-platdata` 节点）：`BT,reset_gpio = <&gpio2 RK_PB7>`（**GPIO2_B7**）、`BT,wake_gpio = <&gpio2 RK_PC2>`（**GPIO2_C2**）、`BT,wake_host_irq = <&gpio2 RK_PC0>`（**GPIO2_C0**）、`uart_rts_gpios = <&gpio2 RK_PB1>`（**GPIO2_B1**）；另有时钟 `ext_clock`（`clocks = <0x145 0x01>`，phandle 0x145 未追，应为 32.768 kHz 时钟源）。
- ⚠️ 厂商用 `compatible = "wlan-platdata"` / `"bluetooth-platdata"`（Rockchip 私有平台节点）→ **主线内核不认这两个 compatible，必须改写为主线写法**。

### 11.2 方案 A：接 `lwfinger/rtl8723ds` 树外驱动

- 仓库：`https://github.com/lwfinger/rtl8723ds`（SDIO 版，**别用成** rtl8723**du**/rtl8723**de** 的 USB/PCIe 版）。
- 本质：基于 Realtek 闭源 `wlan` 驱动改的树外 SDIO 驱动，向上提供 `cfg80211` 接口，需配固件。
- 内核依赖：`CONFIG_WIRELESS=y` / `CONFIG_CFG80211=y` / `CONFIG_MAC80211=y` / `CONFIG_MMC=y` / `CONFIG_MMC_SDHCI=y`，且 sdmmc1 已启用（主线 `rk356x-base.dtsi` 含 dw-mmc）。
- 固件：需要 `/lib/firmware/rtlwifi/rtl8723ds_nic.bin` 与 `rtl8723ds_wowlan.bin`（仓库 `firmware/` 目录自带；`linux-firmware` 不一定含 8723ds 专属）。
- 编译方式（推荐树外 `ko`，别塞进主线树）：
  ```sh
  # 在内核源码树外编译（需已编好的主线内核 + 模块符号）
  make -C /lib/modules/$(uname -r)/build M=$PWD/rtl8723ds modules
  # 产出 8723ds.ko
  cp rtl8723ds.ko /lib/modules/$(uname -r)/kernel/drivers/net/wireless/
  depmod -a && modprobe 8723ds
  ```
- **DTS 改写**（替换厂商私有节点，写进 `rk3568-evb1-v10.dts` 或追加 dtsi）：
  ```dts
  // WiFi SDIO 子节点（挂 sdmmc1）
  &sdmmc1 {
      bus-width = <4>;
      non-removable;
      cap-sdio-irq;
      keep-power-in-suspend;
      sd-uhs-sdr104;
      mmc-pwrseq = <&sdio_pwrseq>;
      status = "okay";
      #address-cells = <1>;
      #size-cells = <0>;
      wifi@1 {
          compatible = "realtek,rtl8723ds";   // 与 lwfinger 驱动 of_match 对应
          reg = <1>;
          interrupt-parent = <&gpio2>;
          interrupts = <RK_PC3 IRQ_TYPE_LEVEL_LOW>;  // GPIO2_C3
      };
  };

  // 上电时序（保留厂商 mmc-pwrseq-simple 语义）
  sdio_pwrseq: sdio-pwrseq {
      compatible = "mmc-pwrseq-simple";
      pinctrl-names = "default";
      pinctrl-0 = <&wifi_enable_h>;          // GPIO2_C4
      reset-gpios = <&gpio2 RK_PC4 GPIO_ACTIVE_LOW>;
      post-power-on-delay-ms = <200>;
  };

  // BT serdev 子节点（替换 bluetooth-platdata）
  &uart8 {
      status = "okay";
      pinctrl-names = "default";
      pinctrl-0 = <&uart8m0_xfer &uart8m0_ctsn &uart8m0_rtsn>;
      bluetooth {
          compatible = "realtek,bluetooth";
          reset-gpios = <&gpio2 RK_PB7 GPIO_ACTIVE_LOW>;       // GPIO2_B7
          device-wake-gpios = <&gpio2 RK_PC2 GPIO_ACTIVE_HIGH>; // GPIO2_C2
          host-wake-gpios = <&gpio2 RK_PC0 GPIO_ACTIVE_HIGH>;   // GPIO2_C0
          clocks = <&your_32k_clock>;  // 映射厂商 ext_clock(phandle 0x145)，多为 32.768kHz 时钟
      };
  };
  ```
- 加载后：`ip link` 应出现 `wlan0`；BT 由内核 `btrtl`/`hci_h5` 经 `realtek,bluetooth` 绑定自动初始化（不一定需要手动 `rtk_hciattach`，但出厂脚本的 `rtk_hciattach -n -s 115200 /dev/ttyS8 rtk` 仍可作为 fallback）。
- ⚠️ **风险/坑**：
  - 树外驱动针对的内核 API（cfg80211 / sdio 回调）可能与 6.18/7.1 有出入，**首次编译大概率要改几处**（如 `cfg80211_scan_done`、`ieee80211_*` 签名变更）——属正常，不是板子问题。
  - 固件缺失会 `request_firmware` 失败 → 先确认 bin 在 `/lib/firmware/rtlwifi/`。
  - `realtek,rtl8723ds` 是 lwfinger 驱动私有 compatible，主线框架不认 → 必须保留该树外驱动，不能"只改 DTS"。

### 11.3 方案 B：放弃 WiFi，先用千兆以太网

- 千兆 PHY **RTL8211F**（RGMII）主线 `dwmac-rk3568` + `rtl821x` **原生支持**，iperf 实测 **942 Mbps**，零额外驱动。
- 代价：板子必须网线连接，失去无线。
- 但你的目标是"学 Linux 命令和系统构建"——WiFi 不是必需，有线完全够用（SSH / 跑服务 / 联网装包）。

### 11.4 决策建议

| 阶段 | 推荐 | 理由 |
|------|------|------|
| 当前学习阶段 | **方案 B**（千兆优先） | 先把 T0/T1 全跑通（含 SSH 联网），WiFi 留到 T2 屏驱动搞定之后 |
| 需要无线时 | **方案 A**（lwfinger/rtl8723ds） | 按 11.2 改 DTS + 编 `8723ds.ko` + 放固件，预计 0.5~1 天（不含调 API 兼容） |
| 不建议 | 把驱动硬改进主线 `drivers/` | 与 `rtw88` 命名/符号冲突多，保持树外 `ko` 最稳 |

---

## 附：提取与验证方法（可复用）

- DTS 来源：`hardware/Device Tree/rk3568.dtb`（从出厂 `boot.img` 提取），用 `dtc -I dtb -O dts` 反编译。
- init 序列解析：`panel-init-sequence` 的 Rockchip 私有格式为每命令 `[type][delay][len][payload...]`：
  - `type 0x05` → DCS 短写、0 参数（如 `0x11`/`0x29`）
  - `type 0x15` → DCS 短写、1 参数（如 `0xB8 0x25`）
  - `type 0x39` → DCS 长写、N 参数（如 `0xB9 F1 12 83`）
  - `delay` 为命令后延时（ms）
- 原理图：用 PyMuPDF 提取 `RK3568 屏幕 V10.pdf`、`RK3568 底板V10.pdf` 文本，逐引脚核对。
- 主线基线：`raw.githubusercontent.com/torvalds/linux/master` 的
  `arch/arm64/boot/dts/rockchip/{rk356x-base.dtsi,rk3568.dtsi,rk3568-evb1-v10.dts}` 与
  `drivers/gpu/drm/panel/panel-himax-*.c`。
