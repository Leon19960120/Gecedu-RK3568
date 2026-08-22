# 01 - 构建与启动

> 状态：启动路径为 `[BSP-5.10 RUNTIME VERIFIED]`；每次重新构建后仍必须复核 DTB 路径。

## SDK 构建

当前构建在 LubanCat SDK 中完成：

```bash
cd ~/lubancat-linux-sdk
./build.sh kernel
```

期望构建配置：

```text
RK_DEFCONFIG=rockchip_rk3568_gec_defconfig
RK_KERNEL_CFG=rockchip_linux_defconfig
RK_KERNEL_DTS=kernel/arch/arm64/boot/dts/rockchip/rk3568-gec-v11-linux.dts
RK_KERNEL_IMG=kernel/arch/arm64/boot/Image
```

额外 SDK 搭建记录见 `../../development/lubancat_sdk_build.md`。

## DTB 验证规则

只修改 source DTS 不够。每次都要确认三层证据：

1. Source DTS：`rk3568-gec-v11-linux.dts` 以及被 include 的 `.dtsi`。
2. Built DTB / FIT：确认生成的 boot image 中确实包含目标 DTB。
3. Running DTB：检查 `/proc/device-tree/model` 和 `/proc/device-tree/compatible`。

期望运行时 model：

```text
Rockchip RK3568 GEC DDR4 V10 Board
```

如果运行时 model 显示 EVB1，说明系统仍在使用错误 DTB 路径，或启动镜像没有更新。

## 启动路径说明

BSP 5.10 的常规验证应使用 SDK / Rockchip 正常启动流程。历史上手动 `mmc read + bootm` 的实验可能绕过 U-Boot 板级初始化，不应作为 BSP 5.10 的常规验证路径。
