# 01 - Rockchip BSP 6.6 内核获取与构建（规划）

> ⚠️ **本文为规划文档，尚未实测成功。** 当前主线 bring-up 在 6.18 上已完成（见 `../mainline-6.18/`），
> 下一步计划转入 Rockchip BSP 6.6 以获得 NPU / 硬解 / 屏 DTS 点亮等能力。
> 未实测前不写为"已完成"。

---

## 1. 为什么要转 BSP 6.6

| 路线 | RK3568 NPU | 屏 | 评价 |
|------|-----------|----|------|
| Mainline 6.6 / 6.18 / 7.x | ❌ 无官方驱动（Rocket 驱动仅 RK3588+） | 需自写 drm_panel 驱动 | 纯学 Linux 够，但无 NPU |
| **Rockchip BSP 6.6** | ✅ in-tree `rknpu` | 厂内 `panel-simple` 补丁解析 `panel-init-sequence` → DTS 点亮 | **NPU + 屏一站式** |

结论：项目需要 NPU → **纯主线不适合**；选 **Rockchip BSP 6.6**（`rockchip-linux/kernel` `develop-6.6`，LTS + in-tree `rknpu` / `rkvdec` / `mpp` / `isp`）。

> 顺带红利：BSP 自带 `panel-simple` 补丁会解析 `panel-init-sequence`，原 mainline 路线最难的 T2 屏驱动
> 直接降为「改 DTS 点亮」，原 `panel-himax-evb1.c` 自定义驱动不再必需。

---

## 2. 仓库与分支

| 项 | 值 |
|----|----|
| 上游仓库 | `https://github.com/rockchip-linux/kernel` |
| 分支 | `develop-6.6`（Rockchip BSP 维护分支，LTS 长期支持，**非** torvalds 主线） |
| 自有 fork / 分支 | 计划 `gecedu-rk3568-6.6`（fork 后新开分支，只提交板级 DTS + defconfig） |

> 重要：要从 `rockchip-linux/kernel` **正经 fork**（GitHub 服务端自带完整历史），不要从空仓库 push——
> 这样后续增量 push 只传 DTS diff（几 KB），避免 mainline 6.18 首次 push 传整树 269 MiB 的坑
> （详见 `../mainline-6.18/10_debug_notes.md` 续9）。

---

## 3. 获取与构建（待执行步骤）

```bash
# 1) fork rockchip-linux/kernel 到自己的账号后 clone
git clone https://github.com/<you>/kernel -b develop-6.6 linux-rk3568-6.6
cd linux-rk3568-6.6

# 2) 交叉编译环境（同 mainline，见 ../mainline-6.18/02_kernel_build.md）
export ARCH=arm64
export CROSS_COMPILE=aarch64-none-linux-gnu-

# 3) defconfig：BSP 通常提供 rockchip 系列 defconfig（如 rockchip_linux_defconfig）
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- rockchip_linux_defconfig

# 4) 编译
make -j$(nproc) ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- Image dtbs
```

> 注：BSP 的 defconfig 命名/路径与 mainline 不同，实际以仓库内 `arch/arm64/configs/` 为准。
> 本步骤尚未在板端验证，命令为预期流程。

---

## 4. 复用 6.18 阶段结论

以下在 **6.18 已验证**，作为 BSP 6.6 的**迁移起点**（DTS 基底不同，落到 6.6 须重新核对节点名/地址，**6.6 尚未验证，不得直接宣称 BSP 6.6 已配置成功**）：

- **以太网（区分 BSP-6.6 BASELINE / GEC PORTING TARGET / GEC BSP-6.6 RUNTIME）**：
  - **BSP-6.6 BASELINE**：Rockchip 官方 `develop-6.6` 的 `rk3568-evb1-v10.dts` 中 `gmac0`=`gmac1`=`okay`，`aliases` `ethernet0=&gmac0` / `ethernet1=&gmac1`。
  - **GEC PORTING TARGET**：`gmac1`(@`fe010000`) = 当前板载以太网口（committed 6.18 DTS `okay`，RTL8211F-CG）；`gmac0`(@`fe2a0000`) = 当前 GEC 板级支持未使用，已审原理图未识别到板载 GMAC0 PHY 连接（不绝对宣称整个硬件层「gmac0 没接 PHY」）。
  - **GEC BSP-6.6 RUNTIME**：尚未验证。
- **USB2**：`usb2phy0/1` + `usb_host0_ehci/ohci`(@`fd800000`/`fd840000`) + `usb_host1_ehci/ohci`(@`fd880000`/`fd8c0000`)。
- **USB3**：`usb_host0_xhci`(@`fcc00000`, `dr_mode="peripheral"`+`extcon`) / `usb_host1_xhci`(@`fd000000`, `dr_mode="host"`)；USB3 SS phy = **`combphy0`(host0) / `combphy1`(host1)**；**本内核树无上游 usbdp phy 节点**。
- I2C2 + BH1750/MPU6050 节点 + 驱动 `=y` → IIO 传感器
- 外置 FIT 打包流程（`mkimage -E -p 0x800`，gzip，truncate 32M）

---

## 5. 待确认 / 风险

- BSP 非纯主线，与上游有差异、部分上游补丁缺失，但 RK3568 资料最全最稳。
- `rknn` 用户态库（`librknnrt`）需另行获取（Rockchip 闭源分发，`airockchip/rknn-toolkit2`）。
- 首次 BSP 启动、NPU 节点验证、屏 DTS 点亮均**待实测**，见 `02_board_dts.md` / `03_rknpu_rknn.md`。
