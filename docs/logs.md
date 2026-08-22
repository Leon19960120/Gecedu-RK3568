# 运行日志

原始 runtime 日志保存在仓库的 `logs/` 目录中。

GitHub Pages 站点主要展示整理后的文档。完整原始日志可在仓库中查看：

- [BSP 5.10 日志目录](https://github.com/Leon19960120/Gecedu-RK3568/tree/main/logs/rockchip-5.10)
- [历史日志目录](https://github.com/Leon19960120/Gecedu-RK3568/tree/main/logs)

可用以下只读脚本从板端收集一致的状态快照：

```bash
sh scripts/check_bsp_5_10.sh
sh scripts/check_i2c_bindings.sh
```
