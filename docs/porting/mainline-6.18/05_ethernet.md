# 05 - 千兆以太网 bring-up（GMAC / RTL8211F）

> 状态：✅ 已验证（2026-08-07，`eth0: Link is Up - 1Gbps/Full`）。
> 这是 mainline 6.18 移植里最关键的"硬件真的通了"证据之一。

---

## 1. 硬件事实（已核对出厂 DTB）

| 项 | 值 |
|----|----|
| 控制器 | `rk_gmac-dwmac` @ `fe010000` |
| mainline 节点 | `&gmac1`（fe010000 即真口，接 RTL8211F；**以 reg 地址判定，不靠标签名**） |
| PHY | RTL8211F-CG（Realtek 千兆 PHY） |
| PHY 地址（MDIO） | `0` |
| 接口 | RGMII |
| 外部时钟 | 125 MHz |
| Reset | `snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>`，`snps,reset-delays-us = <0 20000 100000>` |

---

## 2. 时间线：从"eth0 都不存在"到"1Gbps Link Up"

### 阶段 A：eth0 整个消失（初始 6.18）

- 现象：`ip link` 只有 `lo`；两个网口 LED 都不亮；U-Boot 期也 `Net: No ethernet found`。
- 排查：`/system/lib/modules/` 只有 3 个 4.19.232 ko，无任何 6.18 模块；
  主因待定：① mainline `rk3568-evb1-v10.dts` 未启用 gmac / PHY 接线与粤嵌板不匹配；② defconfig 未编 stmmac。

### 阶段 B：出现 eth0+eth1 双口但都 DOWN

- 重编内核（STMMAC 等 =y 内置）烧入后，`ip link` 出现 `eth0` + `eth1` 双口 → 证明重编 + 重打 FIT + 只烧 boot 成功。
- 但双口均 `state DOWN`、无载波 → MDIO 扫描不到 PHY。

### 阶段 C：根因定位（reset 加错位置）

逐字节核对出厂 `hardware/Device Tree/rk3568.dts` 证明：

- 板载千兆 PHY 实际接在 `ethernet@fe010000` = 主线 `&gmac1`（fe2a0000 = 主线 `&gmac0`，当前 DTS 里 `disabled`，板上没接 PHY）。
- **reset 必须加到 `&gmac1` 的 MAC 节点**（stmmac 的 `stmmac_mdio_reset` 在 MDIO 扫描前 assert/deassert），
  **不是** PHY 子节点；pinctrl 用 `gmac1_*`（非 `gmac0m1_*`）。
- `&gmac0` 设 `disabled`（当前 DTS 未接 PHY，非"幽灵口"表述）。

> 早期曾误判"更可能是缺 DTS 节点"，但板端 `gpiochip3 空` + `MDIO device at address 0 is missing` + eth 全 DOWN，
> 正因 reset 没在 MDIO 扫描前执行。**最终结论：reset 位置错误是主因，而非单纯缺节点。**

### 阶段 D：验证通过 🏁

烧入 `gec-v11` + `gmac1` reset 修复后，6.18 启动日志确认：

```text
Machine model: Rockchip RK3568 GEC V1.1 Board
rk_gmac-dwmac fe010000.ethernet eth0: PHY [stmmac-0:00] driver [RTL8211F Gigabit Ethernet]
eth0: Link is Up - 1Gbps/Full - flow control rx/tx
```

- **单 eth0、无 eth1**（phantom 口消除）。
- 出厂基线对照：4.19.232 下 eth0(fe010000/RTL8211F) 也是 1Gbps Link Up → 两内核都认到同一真口，
  印证 gmac1（fe010000）才是正确映射。

---

## 3. 关键 DTS 片段（`rk3568-gec-v11.dts`）

```dts
&gmac1 {
    status = "okay";
    /* RTL8211F-CG @ MDIO addr 0, RGMII, 125MHz ext clk */
    snps,reset-gpios = <&gpio3 RK_PB5 GPIO_ACTIVE_LOW>;
    snps,reset-delays-us = <0 20000 100000>;
    pinctrl-names = "default";
    pinctrl-0 = <&gmac1_miim &gmac1_tx_bus2 &gmac1_rx_bus2
                 &gmac1_rgmii_clk &gmac1_rgmii_bus>;
};
&gmac0 { status = "disabled"; };   /* 当前 DTS 未接 PHY，非"幽灵口"表述 */
```

内核配置：`CONFIG_STMMAC_ETH=y` / `CONFIG_DWMAC_ROCKCHIP=y` / `CONFIG_REALTEK_PHY=y`（或 `CONFIG_PHYLIB` 自动选）。

---

## 4. 板端验证命令

```bash
ip link                         # 看 eth0 是否存在、是否 UP
cat /sys/kernel/debug/gpio      # 看 gpio-109(snps,reset) out hi
dmesg | grep -iE 'gmac|mdio|phy|rtl'
# 期望: PHY [stmmac-0:00] driver [RTL8211F ...] ; eth0: Link is Up - 1Gbps/Full
```

---

## 5. 排错表

| 现象 | 原因 / 处理 |
|------|------------|
| `ip link` 无 eth0 | defconfig 未编 stmmac / DTS 未 enable `&gmac1` |
| eth0+eth1 双口都 DOWN | reset 加错节点 / 没禁用 `&gmac0`；以 reg 地址 `fe010000` 判定真口 |
| `MDIO device at address 0 is missing` | reset 未在 MDIO 扫描前执行（错放 PHY 子节点或错 MAC） |
| Link 灯不亮 | 检查 125MHz 外部时钟、`snps,reset-delays-us`、RGMII 延时 pinctrl |
