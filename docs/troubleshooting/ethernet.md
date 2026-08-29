# 排障 - Ethernet / 以太网

> **适用范围：Mainline 6.18。** 本页保留 Mainline 专题排障，不代表 BSP 5.10 或 BSP 6.1 的当前状态。
> BSP 5.10 与 BSP 6.1 同等维护；RTL8211F 的各路线状态必须回到对应总览和运行日志确认。
> 6.18 特有结论（如 gmac0/gmac1 命名、reset GPIO 位置）不要直接套用到 5.10。

> 对应 6.18 bring-up 文档：`../porting/mainline-6.18/05_ethernet.md`

---

## 1. `ip link` 完全看不到 eth0

**现象**：`ip link` 只有 `lo`；两网口 LED 不亮；U-Boot 期也 `Net: No ethernet found`。

**可能原因 / 处理**：

1. defconfig 未编入 stmmac：
   ```bash
   grep -E 'CONFIG_STMMAC_ETH|CONFIG_DWMAC_ROCKCHIP|CONFIG_REALTEK_PHY' .config
   # 期望均 =y
   ```
2. `rk3568-gec-v11.dts` 未 enable `&gmac0`：
   ```bash
   cat /sys/firmware/devicetree/base/gmac@fe010000/status 2>/dev/null | tr -d '\0'
   # 期望: okay
   ```

---

## 2. 出现 eth0 + eth1 双口，但都 DOWN、无载波

**现象**：重编烧入后双口出现，但 `ip link` 显示 `state DOWN`，插网线无反应。

**根因**：reset 加错位置 / 误把真口 `gmac1`（`fe010000`）当作需禁用口（实情：`fe010000 = &gmac1` 为真口，`fe2a0000 = &gmac0` 当前 DTS 未接 PHY、disabled）。

**关键修复**：reset 必须加到 **`&gmac1` 的 MAC 节点**（不是 PHY 子节点），并禁用 `&gmac0`：

```dts
&gmac1 {
    status = "okay";
    snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>;
    snps,reset-delays-us = <0 20000 100000>;
    pinctrl-0 = <&gmac1m1_miim &gmac1m1_tx_bus2 &gmac1m1_rx_bus2
                 &gmac1m1_rgmii_clk &gmac1m1_clkinout &gmac1m1_rgmii_bus>;
};
&gmac0 { status = "disabled"; };
```

> 判定真口的依据是 **reg 地址 `fe010000`**（`= 主线 &gmac1`，enabled 真口），不是厂内/旧笔记里把 fe010000 误称的 `gmac0`。
> 完整 committed DTS 片段见 `../porting/mainline-6.18/03_device_tree.md` §2.1。

---

## 3. `MDIO device at address 0 is missing`

**现象**：dmesg 报 MDIO 扫描不到 PHY（address 0）。

**根因**：reset 未在 MDIO 扫描前执行（错放在 PHY 子节点 / 错 MAC）。

**验证修复生效**：

```bash
dmesg | grep -iE 'gmac|mdio|phy|rtl'
# 期望: PHY [stmmac-0:00] driver [RTL8211F Gigabit Ethernet]
cat /sys/kernel/debug/gpio | grep -i mdio   # gpio-109(mdio-reset) out hi
```

---

## 4. Link 灯亮但速度只有 100M / 协商异常

**排查**：
- 125 MHz 外部时钟是否到位（`pinctrl` 含 `gmac0_rgmii_clk`）。
- RGMII 延时 pinctrl 是否完整（`gmac0_rgmii_bus`）。
- `snps,reset-delays-us = <0 20000 100000>` 延时是否足够（RTL8211F 复位需 ~10ms）。

**成功标志**：

```text
eth0: Link is Up - 1Gbps/Full - flow control rx/tx
```
