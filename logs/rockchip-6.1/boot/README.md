# Rockchip BSP 6.1 启动日志索引

本目录只保存原始串口启动证据。纯日志统一使用 `.log`；问题分析、结论和复测路线保存在 `docs/porting/rockchip-6.1/` 的 Markdown 文档中。

## 文件清单

| 文件 | 内核 | 证据范围 | 备注 |
|------|------|----------|------|
| `full_boot_2026-08-27_kernel-6.1.99-13.log` | Linux 6.1.99 #13 | DDR -> U-Boot -> kernel -> init -> HDMI / USB 后续输出 | 完整启动链；末尾包含 USB 枚举失败现场 |
| `kernel_boot_2026-08-28_kernel-6.1.99-18_with-usb-test.log` | Linux 6.1.99 #18 | `Starting kernel` -> init -> CH340 插拔测试 | 不含 DDR / U-Boot，不能当作完整 Bootloader 日志 |
| `full_boot_2026-08-29_kernel-6.1.99-18_serial-cable.log` | Linux 6.1.99 #18 | DDR -> U-Boot -> kernel -> init | 换排线后的 MobaXterm 全串口会话；原始终端字符保持不变 |
| `kernel_boot_2026-08-29_kernel-6.1.99-22.log` | Linux 6.1.99 #22 | `Booting Linux` -> init -> Ethernet / CAN / Bluetooth 后续输出 | 690 行；对应 `10_boot_log_issue_audit_2026-08-29.md` |

## 命名规则

```text
full_boot_YYYY-MM-DD_kernel-VERSION-BUILD[-scenario].log
kernel_boot_YYYY-MM-DD_kernel-VERSION-BUILD[-scenario].log
```

- `full_boot`：必须包含 DDR / miniloader 或 U-Boot 到 Linux 用户空间的启动链。
- `kernel_boot`：从 `Starting kernel`、`Booting Linux` 或内核早期日志开始。
- `scenario`：只记录确实存在的额外场景，例如换串口线或 USB 插拔测试。
- 原始日志不添加 Markdown 围栏，不修正乱码、不删除重复输出，也不混入分析结论。
