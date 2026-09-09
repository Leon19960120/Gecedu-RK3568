# 11 - Ubuntu 22.04 EXTBOOT 移植与图形系统跑通

> 日期：2026-09-06<br>
> 状态：`[BSP-6.1 UBUNTU RUNTIME VERIFIED]`<br>
> 结论：Ubuntu 22.04 XFCE 已能在 GEC RK3568 DDR4 V11 上从 SD 卡稳定启动并进入图形系统。项目由“能否启动”阶段转入外设闭环、首次启动体验和系统优化阶段。

## 1. 当前运行基线

| 项目 | 当前值 |
|------|--------|
| 开发板 | GEC RK3568 DDR4 V11 |
| 架构 | ARM64 |
| 内核 | Linux 6.1.99-rk356x |
| Rootfs | Ubuntu 22.04 XFCE |
| 启动介质 | SD 卡 |
| 启动模式 | `RK_KERNEL_EXTBOOT=y` |
| 专用 defconfig | `rockchip_rk3568_gec_linux_defconfig` |
| 运行 DTB | `rk3568-evb1-gec-v11-linux.dtb` |
| 根分区 | `/dev/mmcblk1p3` |
| Boot 分区 | `/dev/mmcblk1p2`，挂载到 `/boot` |

内核已正确识别板卡：

```text
Machine model: Rockchip RK3568 GEC DDR4 V11 Board
```

Ubuntu 根文件系统和 Boot 分区的实测挂载关系为：

```text
/dev/mmcblk1p3  /
/dev/mmcblk1p2  /boot
```

这些设备名是本次 SD 卡启动环境中的观测值。更换启动介质或调整 MMC 枚举顺序后，应重新通过 `findmnt`、`lsblk` 和内核命令行确认，不能永久假定分区名不变。

## 2. GEC 专用内核和设备树

SDK 当前使用：

```text
rockchip_rk3568_gec_linux_defconfig
rk3568-evb1-gec-v11-linux.dtb
```

启动后 `/boot/rk-kernel.dtb` 的链接目标为：

```text
/boot/rk-kernel.dtb
  -> dtb/rk3568-evb1-gec-v11-linux.dtb
```

结合启动日志中的 `Machine model`，可以确认本次运行系统使用的是 GEC V11 专用 DTB，而不是 LubanCat 通用板卡 DTB。

建议每次更新 Boot 分区后复核：

```bash
readlink -f /boot/rk-kernel.dtb
cat /proc/device-tree/model
uname -a
```

## 3. EXTBOOT 启动链路

本次跑通后的运行链路为：

```text
U-Boot
  -> boot.scr
  -> uEnv/uEnv.txt
  -> Image-6.1.99-rk356x
  -> rk3568-evb1-gec-v11-linux.dtb
  -> initrd.img-6.1.99-rk356x
  -> Ubuntu rootfs (/dev/mmcblk1p3)
```

其中 `boot.cmd` 是启动脚本源码，构建后生成 U-Boot 实际执行的 `boot.scr`。因此源码和运行关系应写成：

```text
boot.cmd --mkimage--> boot.scr --U-Boot executes--> uEnv + Image + DTB + initrd
```

针对 GEC 板卡新增了专用 uEnv 配置，当前链接为：

```text
/boot/uEnv/uEnv.txt
  -> uEnvGEC.txt
```

这使 GEC 的内核、DTB、initrd 和 rootfs 参数能够独立维护，不再借用其他板卡的默认 uEnv。

## 4. 当前 Boot 分区结构

本次验证时的关键文件如下：

```text
/boot
|-- Image -> Image-6.1.99-rk356x
|-- Image-6.1.99-rk356x
|-- initrd -> initrd.img-6.1.99-rk356x
|-- initrd.img-6.1.99-rk356x
|-- rk-kernel.dtb -> dtb/rk3568-evb1-gec-v11-linux.dtb
|-- dtb/
|   `-- rk3568-evb1-gec-v11-linux.dtb
|-- boot.cmd
|-- boot.scr
|-- boot_init
`-- uEnv/
    |-- uEnv.txt -> uEnvGEC.txt
    `-- uEnvGEC.txt
```

EXTBOOT 将内核、DTB、initrd 和启动参数放在独立 Boot 分区中，后续更新这些文件时不必重新制作整个 rootfs 镜像。更新后仍需校验符号链接和实际版本，避免链接仍指向旧内核。

## 5. 内核 DEB 打包问题

EXTBOOT 与 Ubuntu rootfs 的组合要求内核能够生成并安装以下 Debian 包：

```text
linux-image-6.1.99-rk356x_*.deb
linux-headers-6.1.99-rk356x_*.deb
linux-libc-dev_*.deb
```

此前 `bindeb-pkg` 打包流程会错误访问：

```text
uEnv/6.1.99/*.txt
```

而 SDK 的 uEnv 实际按芯片系列组织：

```text
uEnv/rk356x/
```

移除或修正这段与 SDK 目录结构不匹配的复制逻辑后，内核 DEB 已成功生成。安装 `linux-image` 包后，内核模块正确进入：

```text
/lib/modules/6.1.99-rk356x/
```

安装后建议执行以下检查：

```bash
test -d /lib/modules/6.1.99-rk356x
depmod -a 6.1.99-rk356x
ls -l /boot/Image /boot/initrd /boot/rk-kernel.dtb
```

## 6. Ubuntu rootfs 的 ext4 兼容问题

WSL 中 e2fsprogs 1.47.2 默认创建的 ext4 文件系统带有 `orphan_file` 特性，而 Ubuntu 22.04 板端使用的 `resize2fs 1.46.5` 无法识别该特性，导致首次启动自动扩容失败：

```text
resize2fs: Filesystem has unsupported feature(s)
```

制作 rootfs 镜像时禁用该特性：

```bash
mkfs.ext4 -O ^orphan_file <rootfs-image-or-partition>
```

核心原则不是统一宿主机与板端的工具版本，而是让制作端生成的文件系统特性保持在板端 e2fsprogs 能识别的范围内。禁用 `orphan_file` 后，镜像具备与板端旧版 `resize2fs` 继续配合的条件。

首次启动自动扩容仍需单独补充最终验收证据：

```bash
findmnt /
df -h /
sudo resize2fs -P /dev/mmcblk1p3
```

## 7. 图形桌面与自动登录

图形链路已确认运行：

```text
/usr/lib/xorg/Xorg
/usr/sbin/lightdm
/usr/sbin/lightdm-gtk-greeter
```

默认桌面会话为：

```ini
user-session=xubuntu
```

系统为嵌入式触摸屏使用场景配置了 `cat` 用户自动登录，避免登录界面尚无屏幕键盘时无法输入密码。该配置解决的是当前人机交互入口问题，不代表触摸输入和屏幕键盘已经完成验证。

可通过以下命令确认图形服务状态：

```bash
systemctl status display-manager --no-pager
pgrep -a Xorg
pgrep -a lightdm
loginctl list-sessions
```

## 8. 已完成项目

- `[VERIFIED]` RK3568 Linux 6.1.99 内核正常启动。
- `[VERIFIED]` GEC V11 专用 defconfig 和设备树生效。
- `[VERIFIED]` SD 卡 Boot、rootfs 分区识别和挂载正常。
- `[VERIFIED]` Ubuntu 22.04 rootfs 成功进入 systemd 用户空间。
- `[VERIFIED]` Xorg、LightDM 和 XFCE 图形链路运行。
- `[VERIFIED]` 内核 DEB 和模块打包链路跑通。
- `[VERIFIED]` GEC 专用 uEnv 生效。
- `[VERIFIED]` Boot 分区中的内核、DTB 和 initrd 可以独立维护。
- `[VERIFIED]` Ubuntu 22.04 XFCE 已能在 GEC-RK3568 上正常启动并进入桌面。

## 9. 后续工作与证据边界

Ubuntu 图形系统跑通不等于全部板载外设均已完成 Ubuntu 用户空间验收。后续按模块继续补齐：

- `[PENDING]` 验证 Wi-Fi 扫描、关联、DHCP 和实际联网。
- `[PENDING]` 验证蓝牙扫描、配对和目标 profile。
- `[PENDING]` 完善触摸屏屏幕键盘及触摸交互。
- `[PENDING]` 检查 ADB / USB Gadget 的内核配置、configfs 配置和枚举结果。
- `[PENDING]` 验证 rootfs 首次启动自动扩容完整闭环。
- `[PENDING]` 优化启动日志和启动时间。
- `[PENDING]` 整理 GEC 专用 `fire-config` 板卡识别。
- `[PENDING]` DSI LCD 在 BSP 6.1 下仍需实机验证。

## 10. 阶段结论

截至 2026-09-06，GEC RK3568 DDR4 V11 已完成 Linux 6.1.99、GEC 专用 DTB、EXTBOOT、Ubuntu 22.04 rootfs、内核 Debian 包及 XFCE 图形桌面的完整启动闭环。

项目下一阶段的重点是按功能补充运行证据和改善系统体验，不再是解决 Ubuntu 能否启动的问题。
