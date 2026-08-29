# 03 - MIPI-DSI 显示

> 状态：`[BSP-5.10 RUNTIME VERIFIED]`，含 U-Boot 启动 logo。

![BSP 5.10 VOP2 显示路由与 Logo 接力](../../assets/display/bsp5.10-vop2-logo-handoff.png)

## 运行时已验证

BSP 5.10 上 1024x600 MIPI-DSI LCD 已验证：

- `dsi0` 已启用
- `route_dsi0` 已启用
- 4-lane MIPI-DSI
- RGB888
- 1024x600，60 Hz
- 使用 `panel-simple-dsi`
- 背光可用
- panel reset 可用
- DRM bind 成功并注册 `fb0`
- 日志出现 `Update mode to 1024x600p60`
- U-Boot 阶段 DSI logo 已显示成功

期望启动表现：

```text
black screen
→ short flash
→ normal display
```

## 日志解读

`failed to find panel or bridge: -517` 可能在 probe 顺序阶段出现。如果后续日志已经出现 `rockchip-drm`、`dw-mipi-dsi-rockchip`、`panel-simple-dsi`、`fb0` 和最终 DSI link bandwidth，则该 `-517` 属于 probe defer，不是最终 LCD 失败。

loader / kernel logo handoff warning 需要结合 route 和 reserved-memory 证据判断；不要只凭一条 warning 下结论。

## 开机 Logo

最新状态：`[BSP-5.10 RUNTIME VERIFIED]`，开机 logo 已成功显示。

根因不是 panel timing，也不是 DSI PHY，而是 VOP route 分配冲突。当前 DTS 是分层 override 架构：

```text
rk3568-gec-v11.dtsi:424
&route_dsi0 {
    status = "okay";
    connect = <&vp0_out_dsi0>;
};

rk3568-evb-gec.dtsi:1509
&route_hdmi {
    status = "okay";
    connect = <&vp1_out_hdmi>;
};
```

修复后 route 分配：

| route | VP | 状态 |
|-------|----|------|
| `route_dsi0` | VP0 | `okay`，DSI 屏 |
| `route_hdmi` | VP1 | `okay`，未接 HDMI 时 disconnected，无冲突 |

关键 U-Boot 证据：

```text
Rockchip UBOOT DRM driver version: v1.0.1
VOP have 2 active VP
Using display timing dts
dsi@fe060000:  detailed mode clock 51200 kHz
VOP update mode to: 1024x600p60, type: MIPI0 for VP0
VP0 set crtc_clock to 51000KHz
final DSI-Link bandwidth: 336 Mbps x 4
hdmi@fe0a0000 disconnected
```

内核侧仍继续正常绑定：

```text
rockchip-drm display-subsystem: bound fe0a0000.hdmi
rockchip-drm display-subsystem: bound fe060000.dsi
[drm] fb0: rockchipdrmfb frame buffer device
```

### 剩余非致命告警（收尾）

修复后 logo 已完整接力（U-Boot → 内核 → fb0），内核侧只剩两条**非致命**告警：

```text
[drm:init_loader_memory] *ERROR* Reserved logo memory should be aligned as:0x1000,
    cureent is:start[0x000000007df00000] size[0x0000000000197e68]
rockchip-drm display-subsystem: route-hdmi: failed to get logo,offset
...
Freeing drm_logo memory: 1632K
```

逐条解读：

- `Reserved logo memory should be aligned ... size[0x197e68]`：U-Boot 已把 `drm_logo` 填上（`start=0x7df00000` 是 4K 对齐的），只是 **size（0x197e68 ≈ 1.67MB）不是 4K 对齐**触发告警。源码 `rockchip_drm_logo.c:244` 只打日志后继续，logo 照常显示，纯 cosmetic。
- `route-hdmi: failed to get logo,offset`：注意告警从修复前的 `route-dsi0` 变成了 `route-hdmi` —— 说明 **DSI0 已经拿到 logo（交接成功）**，只剩 HDMI（断开、无 logo）还在报。根因是 `route_hdmi` 仍 `status = "okay"`。
- `Freeing drm_logo memory: 1632K`：logo 内存（1632K ≈ 0x197e68）在约 7.7s 被释放，证明「U-Boot 显示 → 内核 DRM 接力 → fb0 接管后释放」全程走通。

**收尾建议**：板子没接 HDMI，把 `rk3568-evb-gec.dtsi` 里 `&route_hdmi` 的 `status = "okay"` 删掉（或改 `disabled`），即可消除 `route-hdmi: failed to get logo,offset` 告警。`size` 4K 对齐告警来自 U-Boot 写 logo 尺寸，不必折腾。

## 历史失败模式

旧失败现象曾表现为：

```text
Reserved logo memory should be aligned as:
0x1000
route-dsi0:
failed to get logo,offset
can't not find any logo display
```

当时容易误判成 reserved-memory / DRM logo 区域问题。最终证明关键冲突在 route 分配：`route_dsi0` 写到了 VP1，而 HDMI route 也在 VP1。把 DSI0 接回 SoC 默认的 VP0 后，U-Boot 重新走 DSI 初始化并显示 logo。
