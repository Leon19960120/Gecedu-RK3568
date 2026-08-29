# BSP 6.1 启动说明与显示调试日志

BSP 6.1 的 boot image 由 LubanCat SDK 生成。生成出的 `boot.img` 不应提交到本目录。

## 每次都要验证

```text
source DTS
→ built DTB/FIT
→ running DTB model and compatible strings
```

期望运行时 model：

```text
Rockchip RK3568 GEC DDR4 V11 Board
```

---

## 2026-08-27 — framebuffer 打不开 / 屏不亮 / HDMI 不显示：根因与修复 ✅

### 现象
- 6.1 启动后 launcher 报 `Error: cannot open framebuffer device: No such file or directory`，屏不亮；插 HDMI 也不显示。

### 早期误判（已推翻）
- 曾以为 `panel-simple-dsi fe060000.dsi.0: Expected bpc in {6,8} but got: 0` 是主因。
- 推翻：bpc=0 仅为警告，panel 仍 probe 成功、DSI 也 bound 成功，与 `/dev/fb0` 缺失无关。可选修复：在 `dsi0_panel` 节点加 `bpc = <8>;`（尚未做）。

### 真因（关键）
6.1 内核 `drivers/gpu/drm/Kconfig` 里 `config DRM_FBDEV_EMULATION` 新增了依赖：

```
depends on FB=y || FB=DRM_KMS_HELPER   # 6.1 新增
default y
```

GEC 用的 `rockchip_rk3568_gec_linux_defconfig` **没有设 `CONFIG_FB`** → 该选项虽 `default y` 也被依赖卡死 → 不编入 → **无 `/dev/fb0`** → launcher 开不了 framebuffer → 屏不亮。

### 为什么 5.10 / 4.19 不用写
- 4.19 / 5.10 的 `DRM_FBDEV_EMULATION` **没有 `depends on FB=y`**，靠 Kconfig 默认直接生效，所以旧版 defconfig 不写 `CONFIG_FB` 也能出 fb0。
- 佐证：4.19 SDK 的 `arch/arm64/configs/rockchip_linux_defconfig`（596 行通用基线）同样没有 `CONFIG_FB` / `CONFIG_DRM_FBDEV_EMULATION` 行，却照样出 fb0——印证是 6.1 Kconfig 依赖变了，不是 GEC defconfig 漏配别的东西。

### 修复
在 `arch/arm64/configs/rockchip_rk3568_gec_linux_defconfig` 末尾加一行：

```
CONFIG_FB=y
```

然后重新生成 `.config` 并完整重编内核 + dtb。注意：build 输出目录的 `.config` 若是旧版，必须先 `make rockchip_rk3568_gec_linux_defconfig` 重新生成，否则改了 defconfig 也不生效。

### 验证（build #13, 2026-08-27 15:06, aarch64 GCC 10.3.1）
```
[drm] fb0: rockchipdrmfb frame buffer device
Starting launcher: The framebuffer device was opened successfully.
1024x600, 32bpp
The framebuffer device was mapped to memory successfully.
rockchip-vop2 fe040000.vop: [drm:vop2_crtc_atomic_enable] Update mode to 800x600p75, type: 11(if:HDMI0...) for vp1 dclk: 49500000
```
- `/dev/fb0` 已生成，launcher 成功打开并映射。
- **HDMI（VP1）正常出图，800x600p75**（fb0 控制台落在 HDMI 上）。

### 关于 DSI（澄清，无需改 DT）
- 板子**实际没接 DSI 屏**（物理未插），所以 "DSI 没接" 是指物理未连接，不是 DT 路由 bug。
- `rk356x.dtsi` 里 `route_dsi0` / `route_dsi1` / `route_hdmi` 在 6.1 **默认都是 `disabled`**；GEC dtsi 只使能了 `route_hdmi`（VP1→HDMI）+ `hdmi_in_vp1`，**没有**使能 `route_dsi0`，`dsi0_in_vp0/vp1` 也保持 disabled。
- 这套状态对"只接 HDMI、DSI 不接"是**正确**的，fb0 走 HDMI 即可。不要为了"修 DSI"去改路由。
- （若以后真要接 DSI 屏，再在 GEC dtsi 加 `&dsi0_in_vp0 { status="okay"; };` + `&route_dsi0 { status="okay"; connect=<&vp0_out_dsi0>; };`。）

### 遗留待办（本次未做）
- [ ] 耳机插拔检测：覆盖成 5.10 的 `simple-audio-card` 后丢了 6.1 的 `multicodecs-card`+`hp-det-gpio`
- [ ] USB gadget：`uac2/mtp/rndis/hid` 的 `functions/...` 创建失败
- [ ] （可选）defconfig 精简：删 6.1 新增、4.19 基线没有的 8 个相机/HDMI-RX 驱动 `IMX415/IMX464/OV13855/OV50C40/SC4336/LT6911UXE/LT7911D/RK628_BT1120`；`MALI400/450/MIDGARD` 保留以对齐 4.19 基线
