# 03 - 设备树（Device Tree）适配

> 核心文档。记录板级 DTS `rk3568-gec-v11.dts` 的来源、已确认的硬件映射，以及适配原则。
> 与 `07_i2c_sensors.md` / `05_ethernet.md` / `06_usb.md` 互补（那些是分主题的 DTS 片段与验证）。

---

## 1. DTS 来源与定位

- **当前板级 DTS**：`rk3568-gec-v11.dts`
  - 属于 **initial board support**（初始板级支持），**不是 complete BSP**。
  - 基于 upstream mainline `rk3568-evb1-v10.dts` 逐步增改而来（粤嵌未改原厂设备树，板子即 Rockchip 官方 EVB1 DDR4 V10）。
- **板子本质**：Rockchip RK3568 EVB1 DDR4 V10（compatible `rockchip,rk3568-evb1-ddr4-v10`）。
- **`gec-v11` 命名由来**：用户为不污染 upstream `rk3568-evb1-v10.dts`，独立新建的粤嵌派生板级文件。
- **Makefile**：在 `arch/arm64/boot/dts/rockchip/Makefile` 增加 `dtb-$(CONFIG_ARCH_ROCKCHIP) += rk3568-gec-v11.dtb`。

> 在 mainline 6.18 路线里这笔 DTS 已提交到 `gecedu-rk3568-v6.18` 分支（commit `ce6fcfba`）。
> 转 BSP 6.6 后需另开分支另写（DTS 基底不同，gmac0 reset / usb2phy / usbdp_phy 等结论可复用）。

---

## 2. 已确认的板级硬件映射

下列映射均从出厂 DTB（`hardware/Device Tree/rk3568.dts`，4.19）逐字节核对，或经实机验证：

### 2.1 千兆以太网（已验证 ✅）

| 项 | 值 |
|----|----|
| 控制器地址 | `fe010000` |
| mainline 节点 | `&gmac1`（fe010000 即真口；**判断依据是 reg 地址不是标签名**） |
| PHY | RTL8211F-CG |
| MDIO 地址 | `0` |
| 接口 | RGMII |
| 外部时钟 | 125 MHz |
| Reset GPIO | `GPIO3_B5`（`gpio3 RK_PB5`，低有效） |

关键 DTS 片段（**来源**：已提交 `gecedu-rk3568-v6.18` 的 `rk3568-gec-v11.dts`，逐字摘录；`Evidence: MAINLINE-6.18`）：

```dts
&gmac1 {
    assigned-clocks = <&cru SCLK_GMAC1_RX_TX>, <&cru SCLK_GMAC1>;
    assigned-clock-parents = <&cru SCLK_GMAC1_RGMII_SPEED>, <&gmac1_clkin>;
    clock_in_out = "input";
    phy-handle = <&rgmii_phy1>;
    phy-mode = "rgmii";
    tx_delay = <0x41>;
    rx_delay = <0x1e>;
    snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>;
    snps,reset-delays-us = <0 20000 100000>;
    pinctrl-names = "default";
    pinctrl-0 = <&gmac1m1_miim
                 &gmac1m1_tx_bus2
                 &gmac1m1_rx_bus2
                 &gmac1m1_rgmii_clk
                 &gmac1m1_clkinout
                 &gmac1m1_rgmii_bus>;
    status = "okay";
};
/* MDIO 总线 1 上的 PHY（reg=0），绑定到上方 phy-handle */
&mdio1 {
    rgmii_phy1: ethernet-phy@0 {
        compatible = "ethernet-phy-ieee802.3-c22";
        reg = <0x0>;
    };
};
/* fe2a0000 = &gmac0：当前板级 DTS 未接 PHY，disabled（非"幽灵口"表述） */
&gmac0 { status = "disabled"; };
```

### 2.2 USB（已验证 ✅，注意 mainline 重组）

| mainline 地址 | 角色 | 说明 |
|----|----|----|
| `fcc00000` | `usb_host0_xhci`（DWC3 DRD） | 物理 **Type-C / OTG / ADB** 口 |
| `fd000000` | `usb_host1_xhci`（DWC3 Host） | 第二路 USB3 Host |
| `fd800000` | `usb_host0_ehci` | USB2 Host EHCI |
| `fd840000` | `usb_host0_ohci` | USB2 Host OHCI |
| `fd880000` | `usb_host1_ehci` | 第二路 EHCI |
| `fd8c0000` | `usb_host1_ohci` | 第二路 OHCI |

> ⚠️ **4.19 与 mainline 地址语义不同**：厂内 4.19 里 `fcc00000` 是 `usbdrd`(OTG dwc3)、`fd000000` 是 Host dwc3；
> mainline 下 `fcc00000` 仍是 **`usb_host0_xhci`(DWC3 DRD)**、`fd000000` 是 **`usb_host1_xhci`(DWC3 Host)**，二者都是 dwc3 控制器。
> `usbdp_phy` **不存在于本内核树**（`gecedu-rk3568-v6.18` 的 `rk3568.dtsi` 里 `usb_host0_xhci` 的 USB3 phy 是 `combphy0`）。
> 修正 USB3 时**不是**「启用 usbdp_phy」，而是确认 `usb_host0_xhci`/`usb_host1_xhci` 已 okay 且 `combphy0` 提供 USB3 SuperSpeed phy。完整 DTS 见 `06_usb.md`。

板级 VBUS GPIO 映射（**NEEDS RE-VERIFICATION** ⚠️，两来源方向相反，本文不取舍）：

| 来源 | HOST 口（`vcc5v0_usb_host`） | OTG 口（`vcc5v0_usb_otg`） |
|------|------------------------------|----------------------------|
| 已提交 DTS `gecedu-rk3568-v6.18`（Evidence: MAINLINE-6.18） | `GPIO0_A6`（gpio0 **RK_PA6**） | `GPIO0_A5`（gpio0 **RK_PA5**） |
| 4.19 出厂 DTS / 日志（Evidence: FACTORY-4.19） | `GPIO0_A5`（4.19 日志 `gpio-6 = vcc5v0_otg` 对应） | `GPIO0_A6` |

> 两来源对 HOST / OTG 的 GPIO 分配**方向相反**，本地无原理图交叉验证时无法判定哪份是物理事实。
> 已提交 DTS 是"当前代码状态"的最高权威，但本板尚无原理图佐证，故两栏**并列**并统一标 `NEEDS RE-VERIFICATION`；**未修改 DTS**。

### 2.3 I2C2（M1，已验证 ✅）

| 项 | 值 | Evidence |
|----|----|----------|
| 控制器地址 | `fe5b0000`（`i2c2`） | MAINLINE-6.18 |
| 引脚 | SDA = `GPIO4_B4`，SCL = `GPIO4_B5`（pinctrl `i2c2m1_xfer`） | MAINLINE-6.18 |
| 时钟频率 | `100 kHz` | MAINLINE-6.18 |
| BH1750（光照） | `0x23`（IIO，采样已验证） | MAINLINE-6.18 ✅ |
| MPU6050（六轴） | `0x69`（IIO，polling/基础采样已验证） | MAINLINE-6.18 ✅ |
| MPU6050 INT | `GPIO3_C7`（`RK_PC7`） | SCHEMATIC |
| EEPROM（BL24C02F） | 原理图 U301，接 `I2C2_SDA_M1`/`I2C2_SCL_M1` | SCHEMATIC |

> **三层事实区分（关键，避免再踩"DTS 没写 = invented"的坑）**：committed DTS 的 `&i2c2` **仅含 `bh1750@23` 与 `mpu6050@69` 两个子节点**，
> 既**没有** EEPROM 节点，也**没有** MPU6050 的 `interrupts` 属性。
> - **committed DTS 代码片段**：要保持与代码一致——无 EEPROM、MPU6050 无 `interrupts`（演示"当前提交代码"就该如此，见 `07_i2c_sensors.md`）。
> - **EEPROM / MPU6050 INT 不是 invented**：底板原理图明确画出 `U301 BL24C02F`（`I2C2_SDA_M1`/`I2C2_SCL_M1`）与 `MPU6050 INT → GPIO3_C7`。
>   故硬件事实表**必须保留**二者，并标 `SCHEMATIC / NOT MODELED IN CURRENT DTS`。
> - **EEPROM I2C 地址 NEEDS VERIFICATION**：未用 `i2cdetect` 或确认 A0/A1/A2 硬件绑法前，**不预设 `0x50`**（24C02 常见地址 ≠ 本板事实）。
> - **MPU6050 中断模式 NOT VERIFIED**：committed DTS 未描述中断，故中断驱动路径未验证；IIO polling 采样已通。

### 2.4 其它映射（committed DTS 与硬件事实区分）

> **三层事实，允许冲突，文档任务是记录冲突而非选一个覆盖另外两个**：
> - **committed DTS** = 当前软件状态（代码写了什么）；
> - **schematic** = 硬件物理设计证据（板子设计成什么）；
> - **runtime test** = 实机验证到的行为（实际跑通到哪步）。
> 未做实机验证的标 `NOT VERIFIED`；DTS 有而 schematic 没有 / schematic 有而 DTS 没建模的，如实标 `NOT MODELED IN CURRENT DTS`。

- **触摸（两层冲突，NEEDS VERIFICATION）**：
  - **Committed Linux 6.18 DTS**（`&i2c1`）：`goodix,gt1151 @0x14`，`irq-gpios = GPIO0_B5`（`RK_PB5`），`reset-gpios = GPIO0_B6`（`RK_PB6`）。
  - **Board schematic signals**：`TP_INT → GPIO3_B3`（`RK_PB3`），`TP_RST → GPIO3_B4`（`RK_PB4`）。
  - 两层 GPIO 分配**不一致**（DTS 写 GPIO0_B5/B6，底板原理图信号 / schematic signals 为 GPIO3_B3/B4），本文**不强行统一**，如实并列。
  - **Validation: NOT VERIFIED** —— 显示/触摸尚未 bring-up 完成，无法判定哪层是实机真实接线。
  - 早期笔记的 `GT911 @0x5d` 与 committed DTS 也不符（INFERRED，已推翻），但**不能**据此把 `GPIO3_B3/B4` 当成"错误"删掉——它来自 SCHEMATIC，与 DTS 同为待验证来源，应标 `SCHEMATIC / NOT MODELED IN CURRENT DTS` 而非"invented"。
- **背光 PWM**：committed DTS 的 `&backlight` 用 `pwms = <&pwm4 ...>`（即内核 `pwm4`）。
  前期"丝印 PWM4 实为内核 pwm5、索引 +1"的说法**与 committed DTS 不符**，以 committed DTS 为准（INFERRED，已推翻）。
- **屏**：committed DTS `&dsi0` 的 `panel@0` compatible = `wanchanglong,w552793baa`, `raydium,rm67200`；7 寸 MIPI-DSI，1024×600@60，4 lane（非 LVDS）。
  （Evidence: MAINLINE-6.18；Validation: **NOT VERIFIED** —— display pipeline 未点亮，详见 `09_known_issues.md` §3。）
- **按键**：6 个，其中 4 个经 ADC0 模拟（`adc-keys`），2 个 GPIO（`gpio_keys_polled`）。

> ⚠️ **GPIO3_B5 资源冲突（NEEDS SCHEMATIC VERIFICATION）**：committed DTS 中
> `&gmac1` 的 `snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>` 与
> `&dsi0` `panel@0` 的 `reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>` **复用同一 GPIO3_B5**。
> 当前 DTS **未改**（保持提交态）；该冲突是否造成 PHY reset 与屏 reset 互相干扰，需原理图佐证，
> 标记为 `NEEDS SCHEMATIC VERIFICATION`，不在此笔修正 DTS。

---

## 3. 适配原则（重要）

> **未验证设备不要为了完整性强行 `status = "okay"`。**

mainline `rk3568.dtsi` 默认禁用一切外设，必须板级 DTS 逐个显式打开 + 对应驱动编入。
但凡没在板端实测过的节点（例如 CAN、USART、某些 sensor），**保持 disabled 或留空**，
宁可功能列表写「⚠️ 未验证」，也不要编造 `okay` 制造"看起来全支持"的假象。

当前已 `okay` 的节点（经实机验证）：`gmac1`(`fe010000`，真口；`gmac0`=`fe2a0000` 当前 DTS 禁用未接 PHY)、`usb2phy0/1`（含 otg/host 子口）、`usb_host0_xhci`(`fcc00000`, DRD/OTG)、
`usb_host1_xhci`(`fd000000`, Host)、`usb_host0/1_ehci/ohci`、`i2c2`（及 bh1750/mpu6050 子节点）。
> 注：`usbdp_phy` 不在本内核树（见上方 §2.2 说明）。

---

## 4. 编译与验证

```bash
# 仅编 dtb（kernel Image 没动时）
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- \
    rockchip/rk3568-gec-v11.dtb

# 板端看 live device tree 实际节点
ls /sys/firmware/devicetree/base/ | grep -iE 'gmac|usb|i2c|can|serial'
cat /sys/firmware/devicetree/base/gmac@fe010000/status 2>/dev/null | tr -d '\0'
```

---

## 5. 已知坑（DTS 层面）

| 坑 | 现象 | 处理 |
|----|------|------|
| `gmac0`/`gmac1` 混淆 | 出现 `eth0`+`eth1` 双口但都 DOWN | 以 reg 地址判定真口：`fe010000`=&gmac1（真口，okay），`fe2a0000`=&gmac0（当前 DTS 未接 PHY，disabled，非"幽灵口"） |
| 背光 PWM 索引 | 屏不亮 | committed DTS 的 `&backlight` 用 `pwms = <&pwm4 ...>`（即内核 `pwm4`）；前期"丝印 PWM4 实为 pwm5、索引 +1"的说法与 committed DTS 不符，以 committed DTS 为准 |
| `usbdp_phy` 误判（历史错误判断/已推翻） | dwc3 `failed to init core` | 本内核树**无 `usbdp_phy`**；`fcc00000`=&usb_host0_xhci(DWC3 DRD)，USB3 SS phy 为 `combphy0`；启用 `usb_host0_xhci`+`combphy0` |
| `panel-init-sequence` 私有属性 | 屏不亮 | 主线 `panel-simple` 忽略该属性；BSP 6.6 路线才靠它点亮（见 `../rockchip-6.6/`） |
| CAN 兼容字符串 | CAN 不 probe | mainline 用 `rockchip,rk3568-canfd`，**不是**厂内 `rockchip,rk3568-can-2.0` |
