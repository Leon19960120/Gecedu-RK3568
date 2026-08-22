# Rockchip Linux 6.6 BSP 移植规划

> ## ⚠️ 暂缓 / 当前未使用
>
> 本路线当前暂缓。现役 BSP bring-up 目标是通过 LubanCat SDK 使用
> **Rockchip Linux 5.10.209**。
>
> 本目录作为未来研究保留。除非后续补充新的硬件证据，否则不要把它当作当前项目路线。

> ## ⚠️ 状态：PLANNED / NOT YET VERIFIED ON HARDWARE
>
> 本文描述**计划**中的 Rockchip BSP 6.6 移植路线。除明确标注「6.18 已验证」的事实外，
> 所有 6.6 板级支持均**未在生产硬件上实测**，不得读作「已跑通」。任何 6.6 相关结论
> 在实机验证前一律标 `PLANNED / NOT VERIFIED`。

---

## 0. 术语约定（统一区分，避免把"计划"写成"已跑通"）

- **BSP-6.6 BASELINE** = Rockchip 官方 `develop-6.6` 源码（如 `rk3568-evb1-v10.dts`）的**当前现状**。
  例：官方基线中 `gmac0` 与 `gmac1` 均为 `status="okay"`，`aliases` 为 `ethernet0=&gmac0` / `ethernet1=&gmac1`。
- **GEC PORTING TARGET** = 根据 6.18 committed DTS + 原理图 + runtime 准备迁移的**目标**（GEC 板最终要达成什么）。
  例：GEC 板实际口为 `gmac1`（committed 6.18 DTS 中 `gmac1` okay / `gmac0` disabled）。
- **GEC BSP-6.6 RUNTIME** = 在 BSP 6.6 上**实机验证后的状态**——目前**尚未验证**。

> 任何涉及 BSP 6.6 的断言，必须明确落在上述三层之一；**不得把 GEC PORTING TARGET 写成 BSP-6.6 BASELINE**。

---

## 1. 为什么考虑 BSP 6.6

主线 Linux（任意版本 6.6 / 6.18 / 7.x）**均无 RK3568 NPU 官方驱动**——主线 "Rocket" NPU 驱动仅支持
RK3588 及更新芯片。项目需要 NPU 推理 → 纯主线不适合。

**Rockchip BSP 6.6** 自带：
- in-tree `rknpu`（`drivers/rknpu/`，DTS `npu@fde40000`）——NPU 推理
- `rkvdec` / `mpp`——硬解
- `rkisp`——ISP
- 厂内 `panel-simple` 补丁解析 `panel-init-sequence`——MIPI-DSI 屏**靠改 DTS 即点亮**，省掉主线路线最难的 T2 自写面板驱动

> 代价：BSP 非纯主线，与 upstream 有差异、部分上游补丁缺失；RK3568 资料最全最稳，可接受。

---

## 2. 官方内核源码

| 项 | 值 |
|----|----|
| 上游仓库 | `https://github.com/rockchip-linux/kernel` |
| 分支 | `develop-6.6`（Rockchip BSP 维护分支，LTS 长期支持，**非** torvalds 主线） |
| 自有 fork / 分支 | 计划 `gecedu-rk3568-6.6`（fork 后新开分支，只提交板级 DTS + defconfig） |

> 要从 `rockchip-linux/kernel` **正经 fork**（GitHub 服务端自带完整历史），不要从空仓库 push——
> 这样后续增量 push 只传 DTS diff（几 KB），避免 mainline 6.18 首次 push 传整树 269 MiB 的坑
> （详见 `../mainline-6.18/10_debug_notes.md` 续9）。

---

## 3. 当前项目状态

| 项目 | 状态 |
|------|------|
| 主线 6.18 bring-up | ✅ **已完成并验证**（USB2/3、以太网 gmac1、I2C 传感器、FIT 启动）；文档见 `../mainline-6.18/` |
| BSP 6.6 内核 | ⏸ **PLANNED**——尚未 fork/clone，未在硬件上启动 |
| BSP 6.6 板级 DTS | ⏸ **PLANNED**——计划以 `rk3568-evb1-v10.dts` 为基底派生 `rk3568-gec-v11.dts` |
| NPU / 屏 DTS 点亮 | ⏸ **PLANNED / NOT VERIFIED**——BSP 自带能力，但本板未实测 |

> 结论：**6.18 是已验证事实；6.6 是计划。** 不要因为 6.6 文档写得详细，就把它当成已跑通。

---

## 4. 可从 mainline 6.18 复用的事实

以下在 **mainline 6.18 已实测验证**，换 BSP 6.6 时作为**迁移起点**（DTS 基底不同，需重新核对节点名/地址）：

- **以太网（区分三层）**：
  - **BSP-6.6 BASELINE**（Rockchip 官方 `develop-6.6` 的 `rk3568-evb1-v10.dts` 现状）：`gmac0` 与 `gmac1` 均 `status="okay"`，`aliases` 为 `ethernet0=&gmac0` / `ethernet1=&gmac1`——官方 EVB 两口都启用。
  - **GEC PORTING TARGET**（依据 6.18 committed DTS + 原理图 + runtime 准备的迁移目标）：`gmac1`(@`fe010000`) = 当前板载以太网口（committed 6.18 DTS 已 `okay`，RTL8211F-CG，千兆）；`gmac0`(@`fe2a0000`) = 当前 GEC 板级支持未使用，已审原理图未识别到板载 GMAC0 PHY 连接（6.18 DTS 中 `disabled`；此为已审范围结论，不绝对宣称整个硬件层「gmac0 没接 PHY」）。
  - **GEC BSP-6.6 RUNTIME**：尚未验证——移植到 BSP 6.6 后 gmac1 是否仍为实际口、是否沿用官方双口基线，待实机确认。
- **USB2**：`usb2phy0/1` + `usb_host0_ehci/ohci`(@`fd800000`/`fd840000`) + `usb_host1_ehci/ohci`(@`fd880000`/`fd8c0000`)。
- **USB3**：`usb_host0_xhci`(@`fcc00000`, DWC3 DRD, `dr_mode="peripheral"`+`extcon`) /
  `usb_host1_xhci`(@`fd000000`, DWC3 Host, `dr_mode="host"`)；USB3 SS phy = **`combphy0`(host0) / `combphy1`(host1)**；
  **本内核树无上游 usbdp phy 节点**，USB3 SS phy 由 `combphy0`(host0) / `combphy1`(host1) 提供。
- **I2C2**：`bh1750@23` + `mpu6050@69`（committed DTS 无 `interrupts` / `mount-matrix`），驱动 `=y` 即可。
- **启动**：外置 FIT 打包（`mkimage -E -p 0x800`，gzip，truncate 32M）+ RKDevTool 只烧 `boot`。

> 这些结论在 6.18 上成立；BSP 6.6 的 dtsi/DTS 节点名与地址可能不同，落到 6.6 时必须重新确认。

---

## 5. BSP 6.6 上必须重新验证的内容

| 项 | 在 6.18 | 在 6.6 需重新确认 |
|----|---------|-------------------|
| 以太网口 | gmac1 已验证千兆 | gmac1 是否仍为实际口、gmac0 是否仍 disabled（DTS 基底不同） |
| USB3 SS phy | combphy0/combphy1 | BSP 6.6 dtsi 中 combo phy 节点名/地址、USB3 控制器地址可能不同 |
| USB3 SS phy | `combphy0`(host0) / `combphy1`(host1)（无上游 usbdp phy 节点） | BSP 6.6 实际节点名/地址以 dtsi 为准 |
| 屏 DTS 点亮 | 主线需自写驱动（未做） | BSP `panel-simple` 补丁能否直接解析厂内 `panel-init-sequence` |
| NPU | 主线无 | BSP in-tree `rknpu` 能否 probe、`/dev/dri/renderD*` 出现 |
| 触摸 / WiFi / 传感器 | 6.18 部分验证 | 驱动与 DTS 在 BSP 6.6 是否同名同址 |

> 原则：**6.18 验证过 ≠ 6.6 自动成立**。每一项在 BSP 6.6 实机上跑通前，状态维持 `NOT VERIFIED`。

---

## 6. 板级 DTS 移植计划

1. fork `rockchip-linux/kernel` → `develop-6.6`，clone 到本地。
2. 以官方 `rk3568-evb1-v10.dts` 为基底，新建粤嵌派生 `rk3568-gec-v11.dts`，只增改粤嵌特有部分。
3. 以太网（**GEC PORTING TARGET**）：以 `gmac1` 为实际口（依据 §4 的 6.18 committed DTS + 原理图 + runtime 结论）；注意官方 **BSP-6.6 BASELINE** 两口都启用，GEC 目标是沿用 gmac1 作为实际口——旧稿把 gmac0 当口、gmac1 关掉的写法是错误的，勿照抄。
4. USB：启用 `usb2phy0/1` + `combphy0/combphy1`（USB3 SS phy 由 combo phy 提供，无上游 usbdp phy 节点）；USB3 控制器地址/角色以 BSP dtsi 为准。
5. 屏：用厂内 `panel-init-sequence`（BSP `panel-simple` 补丁）；背光 PWM 索引仍注意 +1（`pwm5` 非丝印 `pwm4`）。
6. NPU：启用 BSP 自带 `npu@fde40000` 节点。
7. 触摸 GT911 / WiFi RTL8723DS / I2C 传感器：DTS 改写 + 驱动（同 6.18 路线，节点名以 BSP dtsi 为准）。
8. 外置 FIT 打包 + RKDevTool 只烧 `boot`，保留厂商 U-Boot 与 rootfs。

> 全部为**计划**，未实测成功前不写为"已完成"。详细节点表见 `02_board_dts.md`。

---

## 7. RKNPU / RKNN 计划

- **内核侧（BSP 自带）**：`drivers/rknpu/`，DTS `npu@fde40000`，预期 `rknpu.ko` 加载后 `/dev/dri/renderD128` 出现。
- **用户态**：`librknnrt`（Rockchip 闭源分发，随 `airockchip/rknn-toolkit2` 获取）+ `rknn-toolkit2` 做模型转换/推理。
- **验证目标**：跑一个示例推理（如 MobileNet）确认 NPU 实际工作——驱动加载 ≠ 推理可用。
- **状态**：⏸ PLANNED / NOT VERIFIED，详见 `03_rknpu_rknn.md`。

---

## 8. 验证里程碑

- [ ] fork `rockchip-linux/kernel` `develop-6.6` 并 clone
- [ ] 取 BSP defconfig（`arch/arm64/configs/`，如 `rockchip_linux_defconfig`），编译 `Image dtbs`
- [ ] 以 `rk3568-evb1-v10.dts` 为基底派生 `rk3568-gec-v11.dts`
- [ ] 外置 FIT 打包 + RKDevTool 只烧 `boot`，BSP 6.6 首次启动进命令行
- [ ] 以太网 gmac1 千兆验证
- [ ] USB2/USB3 Host 验证（combphy0/combphy1）
- [ ] I2C2 传感器（BH1750 / MPU6050）验证
- [ ] MIPI-DSI 屏 DTS 点亮验证
- [ ] NPU `rknpu.ko` probe + 示例推理通过

> 每个 checkbox 在实机跑通前均为 `NOT VERIFIED`。

---

## 9. 已知未知项

- **VBUS GPIO 冲突（NEEDS RE-VERIFICATION）**：committed DTS `vcc5v0_usb_host`=GPIO0_A6 / `vcc5v0_usb_otg`=GPIO0_A5，
  与 4.19 出厂映射（HOST=A5 / OTG=A6）相反；BSP 6.6 沿用哪份待原理图/实机裁决。
- **GPIO3_B5 冲突（NEEDS SCHEMATIC VERIFICATION）**：gmac1 `snps,reset-gpios` 与 dsi0 面板 `reset-gpios` 同为 `gpio3 RK_PB5`。
- **触摸冲突（NEEDS VERIFICATION）**：committed DTS `gt1151@0x14`+GPIO0_B5/B6 vs 底板原理图 `TP_INT` GPIO3_B3 / `TP_RST` GPIO3_B4。
- **WiFi RTL8723DS**：需树外驱动 `lwfinger/rtl8723ds`（主线/BSP 均无原生），SDIO + UART8，0.5~1 天。
- **BSP 自身差异**：`develop-6.6` 相对 upstream 的 dtsi 差异、defconfig 命名、rknpu DVFS/IOMMU 在 4GB 板上的稳定性，均待实测。

---

## 附：与 6.18 路线的关系

- 6.18 已验证的结论（§4）是 6.6 的**迁移起点**，不是 6.6 的已验证事实。
- 6.18 文档（`../mainline-6.18/`）保持为「已验证」基准；本目录（`rockchip-6.6/`）保持为「规划」。
- 切勿把本目录的计划性描述复制进 6.18 文档，也不要把 6.18 的验证结论直接标注为 6.6 已通过。
