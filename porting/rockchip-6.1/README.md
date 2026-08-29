# Rockchip BSP 6.1 移植资产

本目录保存 GecEdu RK3568 板卡在 BSP 6.1（LubanCat SDK `kernel-6.1`）上的少量、可审阅移植资产。

不要把完整 LubanCat SDK 或 vendor kernel source 复制进本仓库。

## 目录说明

| 目录 | 用途 |
|------|------|
| `configs/` | config fragment 与已验证配置说明 |
| `patches/` | 必要的小补丁或 diff 片段 |
| `boot/` | boot image 说明、启动验证与显示调试日志 |

权威完整 kernel tree 仍以 LubanCat SDK 工作树（`~/lubancat-linux-sdk/kernel-6.1`）为准。
