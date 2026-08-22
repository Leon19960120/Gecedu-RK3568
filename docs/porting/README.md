# docs/porting — 移植文档索引

本目录保存 GecEdu RK3568 项目的 Linux 板级移植文档。完整 vendor kernel source **不放在本仓库**，这里主要保存文档、配置片段、补丁、启动说明和运行证据。

## rockchip-5.10/ — 当前 BSP 移植路线

当前现役路线是通过 LubanCat SDK 使用 Rockchip BSP Linux 5.10.209。

- 权威状态总览：`00_overview.md`
- 完整文件清单：见 `mkdocs.yml` 的 nav（本页不再手工重复列出，避免漏列/漂移）

## rockchip-6.1/ — 最初主攻路线（已放弃）

Rockchip BSP 6.1 是项目**最初的主攻路线**（in-tree rknpu、mpp、rkisp、panel-simple 补丁），投入时间最长，完成了 DTS override 层与内核配置 closure（均编译验证），最终因 NPU 电源域 warm-reset panic（`panic_on_set_idle`）未解决而放弃，转投 5.10。

DTS override 架构与经验已完整迁移到 5.10；NPU 卡点仍是开放问题，排查方向见 `rockchip-6.1/02_npu_pd_warm_reset.md`。

## mainline-6.18/ — 历史学习路线

Mainline 6.18 曾用于学习 upstream 板级启动、FIT 镜像、DTS 适配和早期排障方法。它仍然是有价值的历史记录，但不是当前产品化 BSP 路线。

该目录中的结论应继续标记为 `[MAINLINE-6.18]` 或历史上下文，不要把 6.18 的运行限制改写成 BSP 5.10 的事实。

## rockchip-6.6/ — 暂缓 / 未来研究

Rockchip BSP 6.6 曾作为未来路线调研过，但当前已经暂缓。现役路线仍是 Rockchip BSP Linux 5.10.209。

不要删除 6.6 文档。除非后续补充真实硬件运行证据，否则它们只作为规划和研究笔记。

## 根目录移植资产

- `porting/rockchip-5.10/`：BSP 5.10 config fragment、patch 和 boot 说明。
- `porting/mainline-6.18/boot/fit-image.its`：历史 mainline FIT 打包记录。
- `porting/mainline-6.18/configs/`：mainline 6.18 bring-up 配置检查点。

## 硬件与排障

- 硬件笔记：`docs/hardware/`
- 分主题排障：`docs/troubleshooting/`
