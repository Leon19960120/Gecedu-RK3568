# 02 - Rockchip BSP 6.6 板级 DTS 移植计划（规划）

> ⚠️ **规划文档，尚未实测。** 描述从 `rk3568-evb1-v10.dts` 基底重建粤嵌板级 DTS 的计划。

---

## 1. 基底选择

- BSP 6.6 自带板级 DTS 列表里应有 `rk3568-evb1-v10.dts`（官方 EVB），以此为基底。
- 新建粤嵌派生板级文件（命名待定，如 `rk3568-gec-v11.dts` 或 `rk3568-gec-rk3568-6.6.dts`），
  只增改粤嵌特有部分，**不污染上游**。

---

## 2. 复用 / 新增的 DTS 节点

| 节点 | 来源 | 说明 |
|------|------|------|
| `gmac0` reset + 禁用 `gmac1` | 6.18 已验证 | 千兆网 RTL8211F |
| `usb2phy0/1` + `usb_host0_*` + `usb_host1_*` + `usbdp_phy` | 6.18 已验证 | USB2/USB3 Host |
| I2C2 + BH1750/MPU6050/EEPROM | 6.18 已验证 | IIO 传感器 |
| NPU `npu@fde40000` | **BSP 自带** | `drivers/rknpu/`，启用即可（mainline 无） |
| MIPI-DSI 屏 | **BSP 自带 `panel-simple` 补丁** | 用厂内 `panel-init-sequence` 属性，改 DTS 即点亮（无需自写驱动） |
| 触摸 GT911 | 改 compatible/reg/GPIO | `goodix.c` 原生支持 |
| Wi-Fi RTL8723DS | 改 DTS（SDIO + UART8）+ 树外驱动 | 同 `../mainline-6.18/` 与 `00_overview.md` §11 |

---

## 3. 屏 DTS 点亮（BSP 路线核心红利）

mainline 路线需自写 `drm_panel` 驱动（Himax 定制 IC，密码 `B9 F1 12 83` 不匹主线驱动）；
**BSP 路线**因厂内 `panel-simple` 补丁解析 `panel-init-sequence`，只需把厂商 DTS 的屏节点段
（含 20 条 init 命令）原样接进 `&dsi0` 即可点亮。

> 注意：背光 PWM 索引仍要 +1（`pwm5` 非丝印 `pwm4`），这是硬件事实，与内核基底无关。

---

## 4. 待执行 / 待验证

- [ ] fork BSP 6.6，以 `rk3568-evb1-v10.dts` 为基底新建板级 DTS
- [ ] 复用 6.18 的 gmac0/usb2phy/usbdp_phy 结论
- [ ] 启用 NPU 节点，验证 `rknpu.ko` 加载、`/dev/dri/renderD*` 出现
- [ ] 屏 DTS 点亮验证（亮屏、无偏移/色偏）
- [ ] 触摸 GT911 重编模块加载
- [ ] 外置 FIT 打包 + RKDevTool 只烧 boot，验证 BSP 6.6 启动

> 全部为规划，未实测成功前不写为"已完成"。
