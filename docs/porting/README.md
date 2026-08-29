# docs/porting — 移植文档索引

本目录保存 GecEdu RK3568 项目的 Linux 板级移植文档。完整 vendor kernel source **不放在本仓库**；这里保存的是路线记录、DTS 方法论、配置结论、启动验证和运行证据。

## 当前阅读入口

- **BSP 5.10**：`rockchip-5.10/00_overview.md`
- **BSP 6.1**：`rockchip-6.1/00_overview.md`
- **跨路线方法论**：`dts_porting_methodology.md`
- **GitHub Pages 导航**：以仓库根目录 `mkdocs.yml` 为准

## rockchip-5.10/ — BSP 5.10 移植路线

该路线通过 LubanCat SDK 使用 Rockchip BSP Linux 5.10.209，与 BSP 6.1 同等维护。

该目录包含：

- BSP 5.10 权威状态总览
- 构建与 DTB 验证规则
- Device Tree 证据链
- MIPI-DSI、GT911、I2C/IIO、RTC/EEPROM、PowerKey、CAN、NPU、Wi-Fi 等分主题记录
- 已知问题与调试方法论

后续外设状态应优先更新 `rockchip-5.10/00_overview.md`，避免 README、首页和分章节各自维护一份状态表导致漂移。

## dts_porting_methodology.md — DTS 移植方法论

这是跨路线的 playbook，沉淀 factory 4.19 参考资料、BSP 5.10 与 BSP 6.1 并行移植，以及 Mainline bring-up 中的共性方法：

- 区分共享 Rockchip 基线与可维护的 GEC 派生层，不按 `rk3568-evb1-*` 前缀误判文件归属
- 区分 GEC 硬件、目标 BSP EVB1、factory 4.19 三层快照
- full-path DTB diff 后分类为 `BOARD_DELTA` / `BSP_DRIFT` / `ARTIFACT`
- GPIO 极性、GMAC 命名、Wi-Fi SDMMC、GT911 地址选择等 gotcha

后续迁移 6.6 或新板型时，优先从这里开始读。

## rockchip-6.1/ — BSP 6.1 移植路线

Rockchip BSP 6.1 与 BSP 5.10 同等维护。它带 in-tree `rknpu`、mpp、rkisp 和 Rockchip panel-simple 扩展，当前已完成启动、HDMI、fb0、专用 defconfig 裁剪及多项 USB 实测。

该目录包含：

- DTS override 与板级配置记录。
- 2026-08-24 启动验证。
- 2026-08-27 `CONFIG_FB=y` 恢复 `/dev/fb0`、HDMI 1080p 验证、GEC 专用 defconfig 精简和 LVGL/fbdev 显示记录。
- 长期内核裁剪、USB 拓扑和板级验证日志。
- RTL8723DS 使用内核自带 rtw88 的模块编译、直连传输、固件握手与联网验收步骤。
- RK3568 CAN1 的 6.1 配置符号、DTS、SocketCAN 注册和物理总线验收步骤。
- RTL8723DS Bluetooth 的 RFKill、UART8/H5、固件下载、HCI 注册与扫描验收步骤。
- Linux 6.1.99 #22 的完整启动日志审计、问题归并、处理优先级与复测命令。

当前 6.1 口径：

- `[BSP-6.1 RUNTIME VERIFIED]`：kernel 6.1.99 可启动，GEC 专用 defconfig 生效，HDMI + fb0 已验证。
- `[BSP-6.1 RUNTIME VERIFIED]`：RTL8723DS 的 rtw88 五模块、固件握手和 `wlan0` 注册已验证；Wi-Fi 扫描和联网仍待补证据。
- `[BSP-6.1 RUNTIME VERIFIED]`：RK3568 CAN1 控制器已注册为 `can0`，500 kbit/s 与 200 MHz 时钟已验证；物理总线收发待验证。
- `[BSP-6.1 RUNTIME VERIFIED]`：RTL8723DS Bluetooth 已完成 UART8/H5 固件下载与 `hci0` 注册；扫描、配对和 profile 待验证。
- `[BSP-6.1 BOOT AUDITED]`：#22 启动日志无致命错误；62 行问题型文本归并为 24 个问题族，按功能闭环和配置完整性分级推进。
- `[PENDING]`：DSI LCD 暂未实测；LVGL 固定 1024x600 与 HDMI 1920x1080 framebuffer 的匹配问题待处理。
- `[OPEN]`：NPU warm-reset 风险仍需继续评估，不影响 6.1 作为并行维护路线。

相关可复用资产放在仓库根目录的 `porting/rockchip-6.1/`，包括 config fragment 和 boot 说明。

## mainline-6.18/ — Mainline 参考路线

Mainline 6.18 用于记录 upstream 板级启动、FIT 镜像、DTS 适配和早期排障方法。它是参考路线，不与两条 Rockchip BSP 路线混用状态。

该目录中的结论应继续标记为 `[MAINLINE-6.18]`，不要把 6.18 的运行限制改写成 BSP 5.10 或 BSP 6.1 的事实。

## rockchip-6.6/ — 暂缓 / 未来研究

Rockchip BSP 6.6 曾作为未来路线调研过，但当前暂缓。当前并行维护 BSP 5.10 与 BSP 6.1，不等于 BSP 6.6 已启动。

不要删除 6.6 文档。除非后续补充真实硬件运行证据，否则它们只作为规划和研究笔记。

## 根目录参考文件

本目录根部还保留少量显示相关参考文件：

- `panel-himax-evb1.c`：历史面板驱动 / panel 参考。
- `rk3568-evb1-v10-panel.dts`：历史 panel DTS 参考。

它们不是 BSP 5.10 / 6.1 当前运行 DTS，不应直接当成运行事实；使用时需回到对应路线文档确认上下文。

## 根目录移植资产

与本文档目录对应的可复用资产在仓库根目录 `porting/` 下：

- `porting/rockchip-5.10/`：BSP 5.10 config fragment、patch 和 boot 说明。
- `porting/rockchip-6.1/`：BSP 6.1 config fragment、boot 说明与专用 defconfig 记录。
- `porting/mainline-6.18/boot/fit-image.its`：Mainline FIT 打包记录。
- `porting/mainline-6.18/configs/`：mainline 6.18 bring-up 配置检查点。

## 硬件与排障

- 硬件笔记：`docs/hardware/`
- 分主题排障：`docs/troubleshooting/`
- 原始 / 摘要日志：`logs/`
