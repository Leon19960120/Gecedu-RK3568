# Boot Image 对比报告

本文是临时目录 `tmp_boot_cmp/boot_对比报告.md` 的整理版本。临时目录包含中间解包产物，除非某个证据文件被明确提升为长期资料，否则应继续只保留在本地。

## 关键结论

- 官方镜像 A 是 U-Boot FIT，包含 `fdt`、`kernel` 和 `resource`。
- 自制镜像 B 是 legacy `uImage`，只包含 gzip kernel，没有内嵌 DTB。
- 单纯 kernel config 差异不能解释 NPU / IOMMU / bus 行为。
- DTB 对比发现，官方 DTB 中 `/bus-npu` 为启用状态，而该实验使用的 GEC DTB snapshot 中该节点为 disabled。
- 不应把 4.19 时代的 DTB 与更新的 6.1 kernel 混用；节点命名和驱动预期都可能不同。

## 当前意义

这份报告属于历史开发证据。当前现役路线是通过 LubanCat SDK 使用 BSP 5.10.209。没有当前运行日志时，不要从这份旧 6.1 对比直接推断 BSP 5.10 的 NPU 状态。
