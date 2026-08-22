# 00 - Rockchip BSP 6.1 移植总览

> 状态：`[SUPERSEDED]` —— 这是项目**最初的主攻路线**，投入时间最长，最终因 NPU 电源域 warm-reset 问题放弃，转投 BSP 5.10。
> 本目录记录这段真实经历，避免后续再踩同样的坑。所有 DTS / config 均为「编译验证、运行时未验证」或「板端观察但未解决」，不要读作已跑通。

## 为什么 6.1 是原目标

Rockchip BSP 6.1（`develop-6.1`，内核 6.1.99）自带：

- in-tree `rknpu`（`drivers/rknpu/`，DTS `npu@fde40000`）——NPU 推理
- `rkvdec` / `mpp`——硬解
- `rkisp`——ISP
- 厂内 `panel-simple` 补丁解析 `panel-init-sequence`——MIPI-DSI 屏靠改 DTS 即点亮，省掉主线路线最难的自写面板驱动

而主线 Linux 任何版本均无 RK3568 NPU 官方驱动（主线 "Rocket" NPU 驱动仅支持 RK3588+）。项目需要 NPU → 纯主线不适合，于是选了 BSP 6.1。

## 基线

| 项 | 值 |
|----|----|
| 内核树 | `/home/hyl/rockchip-kernel-6.1`（shallow clone，branch `develop-6.1`） |
| 内核版本 | 6.1.99（LubanCat SDK 的 `kernel-6.1`） |
| 内核配置 | `rockchip_linux_defconfig` + `rk3568.config`（板级 overlay）+ `rk3568-gec.config`（GEC fragment） |
| DTS | `rk3568-gec-linux.dts`（override 层，见 `01_dts_override.md`） |
| 全量构建工具链 | `/opt` GCC 15.2（`aarch64-none-linux-gnu-`） |
| 轻量任务工具链 | 4.19-SDK Linaro GCC 6.3.1（只能 dtc/defconfig/单对象，全量会被 WERROR 卡死） |

## 做了什么（均已「编译验证」，运行时未验证）

1. **DTS override 层**（决策：不改 Rockchip EVB1 原文件）：`rk3568-gec.dtsi` + `rk3568-gec-linux.dts`，覆盖 GMAC/UART/背光/HDMI/USB VBUS/I2C 传感器/触摸/WiFi/BT。详见 `01_dts_override.md`。
2. **内核配置 closure**：5 个外设驱动（GOODIX/BH1750/AT24/MPU6050_I2C/PCF8563）+ RGA 落进 `rk3568-gec.config`。
3. **NPU/PD_NPU 深挖**：定位 warm-reset panic，见 `02_npu_pd_warm_reset.md`。

## 为什么最终放弃（两层卡点）

1. **启动方法错（已解决）**：早期所有自编镜像失败，根因是用 `bootm 0x0a000000 - 0x0b000000` 而非原生 `boot_fit`，导致内核被搬到非法地址 → Synchronous Abort。修法是改用 Rockchip FIT + `boot_fit`。**这一步证明了板子/固件本身没问题**。
2. **6.1 特有的 NPU warm-reset panic（未解决 → 放弃）**：修好启动后，发现 warm reset（`reboot`/复位键）后再启动会在 `rockchip_pd_power_on` → `rockchip_pmu_set_idle_request` 处 `panic_on_set_idle`——PD_NPU 在 warm reset 时粘滞、NIU ACK 不清。**5.10 完全没有这个问题**（冷启 + reset 均正常、NPU 完全可用）。

## 结论与去向

- **6.1 的 DTS override 架构与经验完整迁移到了 5.10**（`rockchip-5.10/` 现役路线的 `rk3568-gec-v11.dtsi` 就是同一套 override 思想）。
- NPU 卡点最终由「换 5.10」绕开，而非在 6.1 里修好——所以 6.1 的 `panic_on_set_idle` 根因**仍是开放问题**，若未来要回 6.1/6.6，`02_npu_pd_warm_reset.md` 里的排查方向是起点。

## 与其它路线的关系

| 路线 | 定位 |
|------|------|
| `rockchip-5.10/` | 现役（继承 6.1 的 DTS override 架构，NPU 正常） |
| `rockchip-6.1/`（本目录） | **真实历史主攻路线**，含 DTS 成果 + NPU 卡点 |
| `mainline-6.18/` | 历史学习路线（无 NPU） |
| `rockchip-6.6/` | 曾规划、从未动手（保留为未来研究） |
