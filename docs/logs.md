# 运行日志

原始 runtime 日志保存在仓库的 `logs/` 目录中。

GitHub Pages 站点主要展示整理后的文档。完整原始日志可在仓库中查看：

- [BSP 5.10 日志目录](https://github.com/Leon19960120/Gecedu-RK3568/tree/main/logs/rockchip-5.10)
- [BSP 6.1 日志目录](https://github.com/Leon19960120/Gecedu-RK3568/tree/main/logs/rockchip-6.1)
- [BSP 6.1 启动日志索引](https://github.com/Leon19960120/Gecedu-RK3568/blob/main/logs/rockchip-6.1/boot/README.md)
- [Linux 6.1.99 #22 内核启动日志](https://github.com/Leon19960120/Gecedu-RK3568/blob/main/logs/rockchip-6.1/boot/kernel_boot_2026-08-29_kernel-6.1.99-22.log)
- [GPIO3_A4 / 4G5G regulator 极性修复证据](https://github.com/Leon19960120/Gecedu-RK3568/blob/main/logs/rockchip-6.1/power/pcie_4g5g_regulator_polarity_2026-08-29.md)
- [历史日志目录](https://github.com/Leon19960120/Gecedu-RK3568/tree/main/logs)

可用以下只读脚本从板端收集一致的状态快照：

```bash
sh scripts/check_bsp_5_10.sh
sh scripts/check_i2c_bindings.sh
```
