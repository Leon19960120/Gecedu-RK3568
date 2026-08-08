# Troubleshooting - Ethernet / 以太网

> 对应 bring-up 文档：`../porting/mainline-6.18/05_ethernet.md`

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

**根因**：reset 加错位置 / 没禁用 `gmac1` 幽灵口。

**关键修复**：reset 必须加到 **`&gmac0` 的 MAC 节点**（不是 PHY 子节点），并禁用 `&gmac1`：

```dts
&gmac0 {
    status = "okay";
    snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>;
    snps,reset-delays-us = <0 20000 100000>;
    pinctrl-0 = <&gmac0_miim &gmac0_tx_bus2 &gmac0_rx_bus2
                 &gmac0_rgmii_clk &gmac0_rgmii_bus>;
};
&gmac1 { status = "disabled"; };
```

> 判定真口的依据是 **reg 地址 `fe010000`**，不是标签名（厂内把 fe010000 标成 "gmac1" 只是命名癖）。

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
