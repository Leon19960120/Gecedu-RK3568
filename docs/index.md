# GecEdu RK3568 BSP 移植文档站

本站记录 **GecEdu / GEC RK3568 V11** 的 Linux BSP bring-up：Device Tree 适配、内核配置、驱动集成、实机验证和调试方法论。

!!! note "当前路线"
    当前现役路线是基于 LubanCat SDK 的 **Rockchip BSP Linux 5.10.209**。Mainline Linux 6.18 保留为历史学习路线，Rockchip BSP 6.6 当前暂缓。

## 当前平台

| 项目 | 值 |
|------|----|
| SoC | Rockchip RK3568 |
| 板卡 | GEC / GecEdu RK3568 V11 |
| 现役内核 | Rockchip BSP Linux 5.10.209 |
| SDK | LubanCat SDK |
| 运行时 model | `Rockchip RK3568 GEC DDR4 V10 Board` |
| 当前 DTS | `rk3568-gec-v11-linux.dts` |

## 移植快照

各外设的权威验证状态见 [BSP 5.10 总览](porting/rockchip-5.10/00_overview.md)，此处不重复维护状态表。

## 推荐阅读顺序

- [BSP 5.10 总览](porting/rockchip-5.10/00_overview.md)
- [构建与启动](porting/rockchip-5.10/01_build_and_boot.md)
- [Device Tree 笔记](porting/rockchip-5.10/02_device_tree.md)
- [调试方法论](porting/rockchip-5.10/11_debug_methodology.md)

## 证据口径

每个设备按最弱成立证据记录：

```text
source DTS
→ built DTB
→ running DTB
→ bus device/client exists
→ driver bound
→ subsystem registered
→ sysfs/dev node exists
→ runtime function verified
```

这是板级 bring-up 和 BSP 集成记录，不声称从零开发驱动，也不声称所有外设完整支持。
