# GecEdu RK3568 BSP 移植文档站

本站记录 **GecEdu / GEC RK3568 V11** 的 Linux BSP bring-up：Device Tree 适配、内核配置、驱动集成、实机验证和调试方法论。

!!! note "当前路线"
    当前并行维护 **Rockchip BSP Linux 5.10.209** 与 **Rockchip BSP Linux 6.1.99**，两条路线地位相同、证据分别记录。Mainline Linux 6.18 作为参考路线保留，Rockchip BSP 6.6 当前暂缓。

## 当前平台

| 项目 | 值 |
|------|----|
| SoC | Rockchip RK3568 |
| 板卡 | GEC / GecEdu RK3568 V11 |
| 并行维护内核 | Rockchip BSP Linux 5.10.209 / 6.1.99 |
| SDK | LubanCat SDK |
| BSP 5.10 DTS | `rk3568-gec-v11-linux.dts` |
| BSP 6.1 DTS | `rk3568-evb1-gec-v11-linux` |

## 移植快照

两条路线的权威验证状态分别见 [BSP 5.10 总览](porting/rockchip-5.10/00_overview.md) 与 [BSP 6.1 总览](porting/rockchip-6.1/00_overview.md)，此处不重复维护状态表。

## 推荐阅读顺序

- [BSP 5.10 总览](porting/rockchip-5.10/00_overview.md)
- [构建与启动](porting/rockchip-5.10/01_build_and_boot.md)
- [Device Tree 笔记](porting/rockchip-5.10/02_device_tree.md)
- [调试方法论](porting/rockchip-5.10/11_debug_methodology.md)
- [BSP 6.1 总览](porting/rockchip-6.1/00_overview.md)
- [BSP 6.1 内核裁剪与验证日志](porting/rockchip-6.1/05_kernel_trim_validation_log.md)

## 证据口径

每个设备按最弱成立证据记录：

![板级 Bring-up 八级证据链](assets/methodology/bringup-evidence-chain.png)

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
