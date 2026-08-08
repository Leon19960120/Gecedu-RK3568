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

关键 DTS 片段（reset 加在 **MAC 节点 `&gmac1`**，不是 PHY 子节点）：

```dts
&gmac1 {
    status = "okay";
    snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>;
    snps,reset-delays-us = <0 20000 100000>;
    pinctrl-names = "default";
    pinctrl-0 = <&gmac1_miim &gmac1_tx_bus2 &gmac1_rx_bus2 &gmac1_rgmii_clk &gmac1_rgmii_bus>;
};
/* fe2a0000 = &gmac0：当前 DTS 未接 PHY，禁用（非"幽灵口"表述） */
&gmac0 { status = "disabled"; };
```

### 2.2 USB（已验证 ✅，注意 mainline 重组）

| mainline 地址 | 角色 | 说明 |
|----|----|----|
| `fcc00000` | `usb_host0_xhci`（DWC3 DRD） | 物理 **Type-C / OTG / ADB** 口 |
| `fd000000` | `usb_host1_xhci`（DWC3 Host） | 第二路 USB3 Host |
| `fd800000` | `usb_host0_ehci` | USB2 Host EHCI |
| `fd840000` | `usb_host0_ohci` | USB2 Host OHCI |
| `fc800000` | `usb_host1_ehci` | 第二路 EHCI |
| `fc840000` | `usb_host1_ohci` | 第二路 OHCI |

> ⚠️ **4.19 与 mainline 地址语义不同**：厂内 4.19 里 `fcc00000` 是 `usbdrd`(OTG dwc3)、`fd000000` 是 Host dwc3；
> mainline 下 `fcc00000` 仍是 **`usb_host0_xhci`(DWC3 DRD)**、`fd000000` 是 **`usb_host1_xhci`(DWC3 Host)**，二者都是 dwc3 控制器。
> `usbdp_phy` **不存在于本内核树**（`gecedu-rk3568-v6.18` 的 `rk3568.dtsi` 里 `usb_host0_xhci` 的 USB3 phy 是 `combphy0`）。
> 修正 USB3 时**不是**「启用 usbdp_phy」，而是确认 `usb_host0_xhci`/`usb_host1_xhci` 已 okay 且 `combphy0` 提供 USB3 SuperSpeed phy。完整 DTS 见 `06_usb.md`。

板级 VBUS GPIO（来自 4.19 DTS，**NEEDS RE-VERIFICATION** ⚠️）：
- HOST：`GPIO0_A5`（**与已提交 DTS 的 `vcc5v0_usb_host`/`vcc5v0_usb_otg` 命名/连接需核对，暂未改 DTS**）
- OTG：`GPIO0_A6`（4.19 日志里 `gpio-6 = vcc5v0_otg` 即此）
> 已提交 `gecedu-rk3568-v6.18` 的 `rk3568-gec-v11.dts` 通过 `usb2phy0_host`/`usb2phy0_otg` 的 `phy-supply = <&vcc5v0_usb_host>/<&vcc5v0_usb_otg>` 供 VBUS，
> 与上面的 4.19 GPIO 编号**可能不一致**，以实际提交 DTS 为准。

### 2.3 I2C2（M1，已验证 ✅）

| 项 | 值 |
|----|----|
| 控制器地址 | `fe5b0000`（`i2c2`，alias `i2c2 = "/i2c@fe5b0000"`） |
| 引脚 | SDA = `GPIO4_B4`，SCL = `GPIO4_B5`（pinctrl `i2c2m1_xfer`，dtsi 自动绑定） |
| BH1750（光照） | `0x23` |
| EEPROM（24C02） | `0x50` |
| MPU6050（六轴） | `0x69`，中断 `GPIO3_C7`（`RK_PC7 IRQ_TYPE_EDGE_RISING`） |

DTS 片段与驱动开启见 `07_i2c_sensors.md`。

### 2.4 其它已确认映射（来自出厂 DTS / 逆向）

- **触摸 GT911**：`i2c1`(`fe5a0000`) `@0x5d`，irq `GPIO3_B3`，rst `GPIO3_B4`（mainline `rk3568-evb1-v10.dts` 写的是 `gt1151 @0x14`，需改；`drivers/input/touchscreen/goodix.c` 原生支持 GT911）。
- **背光 PWM**：原理图丝印 "PWM4"，但 DTS 实测 `fe6e0010` = 内核 **`pwm5`**（主线 `rk3568-evb1-v10.dts` 用 `&pwm4`，迁移时该索引 **+1**）。
- **屏**：7 寸 MIPI-DSI，1024×600@60，4 lane，像素时钟 51.2 MHz（非 LVDS；README 旧 "LVDS" 是错的）。
- **按键**：6 个，其中 4 个经 ADC0 模拟（`adc-keys`），2 个 GPIO（`gpio_keys_polled`）。

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
| 背光 PWM 索引 | 屏不亮，报 PWM 找不到 | 用 `pwm5`（非丝印 pwm4），索引 +1 |
| `usbdp_phy` 误判（历史错误判断/已推翻） | dwc3 `failed to init core` | 本内核树**无 `usbdp_phy`**；`fcc00000`=&usb_host0_xhci(DWC3 DRD)，USB3 SS phy 为 `combphy0`；启用 `usb_host0_xhci`+`combphy0` |
| `panel-init-sequence` 私有属性 | 屏不亮 | 主线 `panel-simple` 忽略该属性；BSP 6.6 路线才靠它点亮（见 `../rockchip-6.6/`） |
| CAN 兼容字符串 | CAN 不 probe | mainline 用 `rockchip,rk3568-canfd`，**不是**厂内 `rockchip,rk3568-can-2.0` |
