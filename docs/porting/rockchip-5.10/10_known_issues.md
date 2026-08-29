# 10 - 已知问题

> 本页只放**未解决**或**已解决（历史）**问题。当前进度/状态以 `00_overview.md` 为权威，不在此重复维护。

## 当前待处理

| 问题 | 状态 | 备注 |
|------|------|------|
| Wi-Fi RTL8723DS 扫描 / 联网 | `[PENDING]` | SDIO、电源时序、`8723ds.ko` 模块加载和 `wlan0` / `p2p0` 注册已成功；下一步是用 `iw` / `wpa_supplicant` 扫描、关联并通过 DHCP 拿 IP。 |
| BT 设备确认 | `[PENDING]` | `[BT_RFKILL]` 已解析 GPIO 并注册 `bt_default`，通用 `hci_uart`（H4/H5）已加载；但 `hci0` 未创建、Realtek RTL / UART8 绑定未完成。当前 DTB 仍走厂商 `wireless-bluetooth` / `rfkill_rk` 兼容层。 |
| CAN1 实际收发 | `[PENDING]` | `CAN device driver interface` 已出现（`CONFIG_CAN_RK3568=y` 在 defconfig，但当前 `.config` 未生效、`can0/can1` 未出现）；需确认 `ip link` 并完成 SocketCAN runtime verification。 |
| NPU RKNN 推理 | `[PENDING / IN PROGRESS]` | RKNPU kernel driver 与 IOMMU path 已 probe；RKNN 用户态模型加载 / 推理仍需证据。 |
| PCF8563 alarm | `[PENDING]` | RTC 已注册为 `rtc1`，但 `invalid alarm value` 仍需跟踪。 |
| RK817 battery / charger warnings | `[PENDING]` | 可能是板级 DT / 硬件装配差异，不代表整个 PMIC 失败。 |
| Headset | `[NEEDS VERIFICATION]` | 写成完整功能前，需要检查最终 DTS 和运行日志。 |
| rootfs init 脚本 bug | `[PENDING]` | `S32load_ts_modules` 第 21 行 `/*insmod`（注释前缀漏进命令）；`S36load_wifi_modules` 第 43 行 `//insmod`（双斜杠）且 rfkill state 路径 `rfkill1/state` 不存在。重烧 boot.img 后 `8723ds.ko` 需重新拷贝到 `/system/lib/modules/`。 |

## 已解决 / 历史问题

| 问题 | 状态 | 结论 |
|------|------|------|
| GT911 触摸 | `[BSP-5.10 RUNTIME VERIFIED]` | I2C1 `0x5d` probe，`ID 911, version 1060`，注册 input（`Goodix Capacitive TouchScreen`）。`goodix_911_cfg.bin` firmware 缺失为非致命，使用默认值。 |
| Stale DTB path | `[SUPERSEDED]` | 运行时 model 显示 EVB1 说明 DTB 错误或过期，不代表目标 GEC bring-up。 |
| DSI route VP 冲突 | `[SUPERSEDED]` | `route_dsi0` 曾误接 `vp1_out_dsi0`，与 `route_hdmi` 的 VP1 分配冲突；现已改回 `vp0_out_dsi0`，U-Boot logo 成功。 |

Mainline 6.18 参考笔记和 BSP 6.6 暂缓笔记继续保留。遇到结论冲突时，应标明具体内核路线，不要改写为 BSP 5.10 事实；BSP 6.1 的状态由其独立文档维护。
