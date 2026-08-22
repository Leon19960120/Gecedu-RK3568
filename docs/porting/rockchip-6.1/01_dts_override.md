# 01 - 6.1 DTS override 层

> 状态：`[BSP-6.1 COMPILE VERIFIED / RUNTIME NOT VERIFIED]` —— 所有 override 都编译并反编译核对过，但**从未在板上实测**（因启动方法 + NPU 卡点，6.1 一直没跑到验证外设那一步）。

## 规划顺序与写法

先讲「6.1 DTS 应该怎么规划、怎么写」，再讲下面的架构与落盘记录。

**规划顺序（5 步）**：

```text
① 建立「GEC 硬件 vs 6.1 EVB1」三层快照
   反编译 GEC factory DTB + 读 6.1 EVB1 dtsi → full-path diff → 分类
   （BOARD_DELTA 落盘 / BSP_DRIFT 不落盘 / ARTIFACT 忽略；方法见 dts_porting_methodology.md §2-3）

② 定 override 架构
   rk3568-gec.dtsi + rk3568-gec-linux.dts 薄入口 + Makefile 一行（见下「架构决策」）

③ 按优先级分批写，每批编译 + 反编译核对
   batch1 基础外设（GMAC/背光/USB VBUS/I2C 传感器/触摸基础）
   → batch2 触摸 GT911
   → batch3 WiFi（SDMMC1，rtl8723ds）
   → batch4 BT（UART8，rtl8723ds）

④ config closure：rockchip_linux_defconfig + rk3568.config + rk3568-gec.config
   5 个外设驱动 =y（GOODIX/BH1750/AT24/MPU6050/PCF8563）+ RGA（见「内核配置 closure」）

⑤ 已知风险先挂起，不阻塞主线
   WiFi 驱动在 6.1 树无源码 → SUSPENDED；camera IMX327 风险大 → 暂缓
```

**写法要点**：

1. **只写差异、不抄默认**：EVB1 已继承且 GEC 一致的不重复写（如 HDMI 三件套、UART8/M0/clocks）。
2. **判断靠反编译核对，不靠肉眼**：每个 batch 编译后 `dtc` 反编译，确认节点/属性与预期一致（如 gt1x 删除后 count=0、GPIO 元组解析正确）。
3. **对照 gotcha 表**：GPIO 极性（flag 0=HIGH/1=LOW）、GMAC 命名（reg 地址为准）、goodix vs gt1x 属性命名等，见 `dts_porting_methodology.md` §5/§7。
4. **不写「不是差异」的东西**：BSP_DRIFT（版本演进）、ARTIFACT（phandle 重编号）一律不落盘。

## 架构决策：override 层，不改 Rockchip 原文件

**关键前提**：`4.19 EVB1 ≠ 6.1 EVB1`。Rockchip 在版本间改动了真实板级配置：

- GMAC delay：4.19 的 `0x41/0x1e` → 6.1 EVB1 的 `0x4f/0x26`
- WiFi 挂载：4.19 EVB1 在 `sdmmc2`，GEC 实际在 `sdmmc1`
- camera sensor 集合、i2c2 传感器（4.19 有、6.1 EVB1 已删）都变了
- NPU 节点从 `rk3568.dtsi` 挪到 `rk356x.dtsi`

所以 GEC 的 6.1 override 必须描述「**GEC 硬件 vs 6.1 EVB1**」的差异，**不能盲抄 4.19 的 GEC DT**。

**文件布局**（`kernel/arch/arm64/boot/dts/rockchip/`）：

```text
rk3568-evb1-ddr4-v10.dtsi   ← Rockchip 6.1 原文件，不动
rk3568-linux.dtsi           ← Rockchip 6.1 原文件，不动
rk3568-gec.dtsi             ← GEC override 层（唯一改动文件）
rk3568-gec-linux.dts        ← 薄入口：#include evb1 dtsi + linux dtsi + gec.dtsi
```

外加 Makefile 一行：`dtb-$(CONFIG_ARCH_ROCKCHIP) += rk3568-gec-linux.dtb`。

**Override 三类动作**：

1. **覆盖值**（override）——如 `gmac1` `clock_in_out` output→input
2. **禁用错误继承**（disable wrong EVB default）——如 `&sdmmc2 { status="disabled" }`（GEC WiFi 在 SDMMC1，不是 EVB1 的 SDMMC2）
3. **补回独有节点**（re-add GEC-only）——如 i2c2 的 BH1750/EEPROM/MPU6050

## 各 batch 落盘内容（均反编译核对通过）

### batch 基础外设

| 节点 | 落盘内容 |
|------|---------|
| `&gmac1` | `clock_in_out="input"`、`tx_delay=<0x41>`、`rx_delay=<0x1e>`、`snps,reset-gpio=<&gpio3 RK_PB5 GPIO_ACTIVE_LOW>`；M1 pinctrl + reset-active-low + reset-delays 继承 6.1 EVB1 不重复 |
| `&uart3` | `status="okay"`（M0 pinctrl 继承） |
| `&backlight` | `pwms=<&pwm4 0 1000000 0>`（1kHz） |
| HDMI 三件套 | 继承 EVB1 已 `okay`，不写 override |
| USB VBUS | `vcc5v0_host` 删 gpio/pinctrl（常开）；`vcc5v0_otg` gpio=A6 + boot-on + always-on + 保留 enable-active-high；`vcc5v0_otg_en` pins A6 |
| `&i2c2` | `status="okay"`、`pinctrl-0=<&i2c2m1_xfer>` + `bh1750@23` / `eeprom@50`(atmel,24c02) / `mpu6050@69`(invensense,mpu6050, interrupt GPIO3_B7, mount-matrix) |
| `&i2c0` | 加 `pcf8563@51` |

> 明确**不写**（正确）：NPU（EVB1 已 enable，继承）、PCIe3x2、CAN1（保持 disabled）、DSI0、触摸/WiFi/BT（batch 2）。

### batch Touch（GT911）

- `&i2c1 { /delete-node/ gt1x@14; }` 删 EVB1 的 `goodix,gt1x`。
- 加 `gt911@5d`：`compatible="goodix,gt911"`、`reg=<0x5d>`、`interrupt-parent=<&gpio3>`、`interrupts=<RK_PB3 IRQ_TYPE_EDGE_FALLING>`、`irq-gpios=<&gpio3 RK_PB3 GPIO_ACTIVE_HIGH>`、`reset-gpios=<&gpio3 RK_PB4 GPIO_ACTIVE_HIGH>`。

**关键驱动发现**：

1. 6.1 `drivers/input/touchscreen/goodix.c`（goodix,gt911）**不调用 `gpiod_to_irq`**——它用 `client->irq`（来自 `interrupts` 属性）。所以节点**必须**带 `interrupt-parent`+`interrupts`，光 `irq-gpios` 不够。
2. **`irq-gpios` 极性必须是 `GPIO_ACTIVE_HIGH`（flag 0）**：goodix 地址选择 `gpiod_direction_output(gpiod_int, addr==0x14)`，`reg=0x5d` ⇒ 输出逻辑 0，要映射到物理 LOW 选 0x5d 就需 ACTIVE_HIGH（polarity-inverted）。当初写成 ACTIVE_LOW 是错的，已改回。
3. 厂内 GT911 用 `irq-gpios`/`reset-gpios`（主 line goodix.c 命名），**不是** `gt1x` 的 `goodix,irq-gpio`/`goodix,rst-gpio`。

### batch WiFi（rtl8723ds，SDMMC1）

- `&sdmmc2 { status="disabled"; }`（EVB1 默认 WiFi 在 sdmmc2，GEC 不用）。
- `&sdmmc1` 开 SDIO：`no-sd; no-mmc;`、`bus-width=4`、`mmc-pwrseq=<&sdio_pwrseq>`、`non-removable`、pinctrl `sdmmc1_bus4/cmd/clk`（gpio2 A3–B0）、`sd-uhs-sdr104`、`status="okay"`。
- `&sdio_pwrseq`：删继承的 `clocks`/`clock-names`（GEC 无），`reset-gpios=<&gpio2 RK_PC4 GPIO_ACTIVE_LOW>`。
- `&wireless_wlan`：`wifi_chip_type="rtl8723ds"`、`WIFI,host_wake_irq=<&gpio2 RK_PC3 GPIO_ACTIVE_HIGH>`、**删继承的 `WIFI,poweren_gpio`**（EVB1 的 gpio3 PD5，GEC 无，避免双重控电）。

### batch Bluetooth（rtl8723ds，UART8）

UART8/M0/`uart_rts_gpios`/`clocks` 已与 GEC 一致 → 继承，只覆盖 3 个不同 GPIO：

```dts
&wireless_bluetooth {
	BT,reset_gpio    = <&gpio2 RK_PB7 GPIO_ACTIVE_HIGH>;
	BT,wake_gpio     = <&gpio2 RK_PC2 GPIO_ACTIVE_HIGH>;
	BT,wake_host_irq = <&gpio2 RK_PC0 GPIO_ACTIVE_HIGH>;
};
```

## 内核配置 closure

生成流程（`rockchip_linux_defconfig` + `rk3568.config` + `rk3568-gec.config`）：

```bash
make ARCH=arm64 CROSS_COMPILE=<tc> rockchip_linux_defconfig
scripts/kconfig/merge_config.sh -m -r .config arch/arm64/configs/rk3568.config arch/arm64/configs/rk3568-gec.config
make ARCH=arm64 CROSS_COMPILE=<tc> olddefconfig
```

`rk3568-gec.config`（6 行，唯一编辑的 fragment）：

```text
CONFIG_TOUCHSCREEN_GOODIX=y
CONFIG_BH1750=y
CONFIG_EEPROM_AT24=y
CONFIG_INV_MPU6050_I2C=y
CONFIG_RTC_DRV_PCF8563=y
CONFIG_ROCKCHIP_RGA=y
```

**RTL8723DS 驱动在 6.1 树里无源码**（`drivers/net/wireless` / `staging` 0 命中），WiFi 驱动 sourcing **SUSPENDED**——这是另一个隐性问题（DTS 就绪、SDMMC1 就绪、RFKILL 就绪，唯独缺驱动）。

## 工具链教训

- **全量 `Image` 构建**：必须用 `/opt` GCC 15.2（`aarch64-none-linux-gnu-`）。4.19-SDK 的 GCC 6.3.1 + `CONFIG_WERROR=y` 会在无关警告上卡死。
- **轻量任务**（dtc / defconfig / 单对象）：可用 4.19-SDK GCC 6.3.1。
