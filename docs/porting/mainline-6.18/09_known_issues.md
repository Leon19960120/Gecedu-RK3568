# 09 - 已知问题 / 未完成项（Known Issues）

> 本文档专门记录**未解决 / 未完成**的问题，避免 README 给人"什么都完成了"的错觉。
> 语气：诚实标注 ✅ 已通 / ⚠️ 部分 / ❌ 未完成。

---

## 1. 未完成功能总览

| 功能 | 状态 | 说明 |
|------|------|------|
| Wi-Fi（RTL8723DS） | ❌ | 原 4.19 `8723ds.ko` 无法用于 6.18；需树外驱动重编 |
| 显示（MIPI-DSI 屏） | ⚠️ | framebuffer / display pipeline 未完成；BSP 6.6 路线可改 DTS 点亮 |
| 触摸（GT911） | ⚠️ | 驱动主线已有，但 6.18 下 `goodix.ko` 版本错未加载；需重编模块 |
| ADB Gadget | ⚠️ | kernel gadget 路径已通，userspace `adbd` 未完全收口 |
| NPU | ❌ | mainline 6.18 路线暂不继续 → 转 Rockchip BSP 6.6 |
| GPU / VPU | ⚠️ | Panfrost（GPU）已开；硬件视频编解码（rkvdec/vepu）未完整验证 |
| CAN | ❌（待验证） | 出厂 DTS 三控制器全 disabled；mainline 兼容 `canfd`，需板级打开 |
| USART（用户串口） | ❌（待验证） | uart1/3/4/8 在 6.18 下大概率未 `okay`；需板级打开 |

---

## 2. Wi-Fi：RTL8723DS（Fn-Link FG6223）

- 模组 = **RTL8723DS**（WiFi 2.4G 走 **SDIO**，BT 走 **UART**）。
- 出厂驱动 `8723ds.ko` 是 4.19 专用树外驱动；主线 **没有** 原生 RTL8723DS 驱动（`rtw88` 系列不支持 8723DS）。
- 6.18 下直接 `insmod` 报 `invalid module format`（模块结构随内核版本变）。
- 可行方案：`lwfinger/rtl8723ds` 树外仓库，针对 6.18 重新编译为 `8723ds.ko` + 放固件
  （`/lib/firmware/rtlwifi/rtl8723ds_nic.bin`）。完整 DTS 改写与坑见 `../rockchip-6.6/00_overview.md` §11（该节对 BSP / mainline 均适用）。
- 当前策略：**先靠千兆以太网**（RTL8211F 主线原生，实测 ~942 Mbps）过渡，Wi-Fi 留到后期。

---

## 3. 显示：MIPI-DSI 屏

- 7 寸 MIPI-DSI，1024×600@60，4 lane（非 LVDS）。
- mainline 6.18 路线：屏 IC 是定制 Himax，SETEXTC 密码 `B9 F1 12 83` 与所有主线 himax 驱动均不匹配
  → 需自写 `drm_panel` 驱动（骨架见 `../panel-himax-evb1.c` / `rk3568-evb1-v10-panel.dts`）。
- 现象：6.18 启动后 `cannot open framebuffer device`；VOP/DSI/HDMI/GPU `sync_state() pending`。
- **BSP 6.6 路线化解**：厂内 `panel-simple` 补丁解析 `panel-init-sequence` → **改 DTS 即点亮**，无需自写驱动。
- 背光 PWM 索引坑：原理图 "PWM4" 实为内核 `pwm5`，迁移时索引 +1。

---

## 4. ADB Gadget

- 已验证：`/sys/class/udc/` 下 Type-C/OTG dwc3 UDC 存在；configfs / FunctionFS 可建立。
- 未收口：出厂 Buildroot 的 `/usr/bin/adbd` userspace 行为 + `S50usbdevice` 脚本反复找
  `/sys/kernel/config/usb_gadget/rockchip`（configfs 未挂载 + 内核未开 `CONFIG_USB_CONFIGFS`/`FUNCTIONFS`）
  → 全部 `No such file or directory`。
- **不要写成 USB Gadget 驱动完全失败**——kernel gadget 路径是通的，只差 userspace 收尾。

---

## 5. NPU

- **不是单纯"失败"**：Mainline Linux 6.18（以及任何 mainline 版本 6.6/6.18/7.x）**均无 RK3568 NPU 官方驱动**
  （主线 "Rocket" 驱动仅支持 RK3588 及更新芯片）。
- 结论：Mainline 6.18 的 NPU 集成暂缓，后续计划转入 **Rockchip Linux 6.6 BSP**，
  使用 Rockchip **RKNPU / RKNN** vendor stack（详见 `../rockchip-6.6/03_rknpu_rknn.md`）。

---

## 6. 触摸 / GPU / VPU

- 触摸 GT911：`drivers/input/touchscreen/goodix.c` 原生支持，只需改 DTS（compatible + reg + GPIO）
  并为 6.18 重编 `goodix.ko` 替换出厂 4.19 版本。
- GPU：Panfrost 已 `=y` 打开，可跑开源 Mesa；但未做实测渲染。
- VPU：硬件视频编解码（rkvdec / vepu）在 mainline 支持度有限，BSP 6.6 路线更完整（rkvdec/MPP）。

---

## 7. 启动后非致命报错（参考）

6.18 启动日志里这批报错**均不阻止进系统**，属"出厂 4.19 rootfs 跑 6.18 内核"的必然摩擦：

| 报错 | 原因 | 影响 |
|------|------|------|
| `goodix.ko` / `8723ds.ko: invalid module format` | 4.19 旧 .ko 塞进 6.18 | 触摸 + WiFi 暂不可用 |
| `cannot open framebuffer device` | 屏驱动未做 | 屏幕不亮 |
| `dwc3: failed to initialize core`（早期） | usb2phy / combphy0 未启用（注：本树无 `usbdp_phy`，旧文档"启用 usbdp_phy"为历史错误判断/已推翻） | USB3 暂不能用（修后已通） |
| configfs 未挂载 | 内核未编 configfs | adb gadget 不可用 |
| `Wrong fs type(ext2)` for oem/userdata | fstab 当 ext2 实际非 | 非致命 |
| `udevd: specified group 'kvm' unknown` | rootfs 无 kvm 组 | 非致命 |
