# 04 - 根文件系统兼容（64-bit kernel + 32-bit userspace）

> 一个很有价值的坑：出厂 Buildroot 是 **32-bit AArch32** 用户态，而我们的内核是 **64-bit ARM64**。
> 必须打开 `CONFIG_COMPAT`，否则用户态起不来。

---

## 1. 问题背景

板子出厂系统是 Buildroot **2018.02-rc3**，用户态二进制是 **AArch32（ARM 32-bit）** 编译的
（出厂 `os-release`：`VERSION=2018.02-rc3-dirty`，`KERNEL="4.19 - rockchip_linux_defconfig"`）。

我们编译的内核是 **ARM64（AArch64）**。64-bit 内核默认**不能**直接执行 32-bit 用户态程序，
除非内核开启 `CONFIG_COMPAT`（提供 32-bit 系统调用兼容层）。

> 这不是板子特例，是所有「64-bit kernel 跑旧 32-bit rootfs」都会遇到的问题。

---

## 2. 根因与修复

| 项 | 说明 |
|----|------|
| 现象 | 不打开 `CONFIG_COMPAT` 时，`/sbin/init` 及所有 32-bit 程序无法执行 → 内核 panic 或卡在 early userland |
| 修复 | 内核 `.config` 打开 `CONFIG_COMPAT=y` |
| 验证 | 打开后 6.18 内核成功跑起出厂 32-bit Buildroot rootfs，`uname -a` 正常、`/bin/sh` 可用 |

```bash
./scripts/config --enable CONFIG_COMPAT
make ARCH=arm64 CROSS_COMPILE=aarch64-none-linux-gnu- olddefconfig
grep CONFIG_COMPAT .config   # 期望: CONFIG_COMPAT=y
```

---

## 3. 启动参数（bootargs）

出厂 rootfs 通过 **PARTUUID** 挂载，与内核版本无关（4.19 / 6.18 都能解析）：

```text
console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait
```

| 参数 | 含义 |
|------|------|
| `console=ttyS2,1500000` | 调试串口（主线无 fiq-debugger，用 `ttyS2` = uart2；波特率 1500000） |
| `root=PARTUUID=614e0000-0000` | 指向 rootfs 分区（出厂 rootfs 的 PARTUUID 恒为该值） |
| `rw rootwait` | 可读写、等待块设备就绪 |

> 实测：6.18 启动日志 `[ 0.000000] Kernel command line: console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait`
> → `[ 1.008170] VFS: Mounted root (ext4 filesystem) on device 179:6` → `Run /sbin/init` 成功。
> 注意 4.19 出厂的 PARTUUID 是短形式 `614e0000-0000`，6.18 某次启动也出现过完整 GUID 形式，两种都能解析到 p6，无需担心。

---

## 4. 一个重要事实：出厂 rootfs 不装 `/lib/modules`

早期误判「rootfs 只有 4.19.232 模块、需要先装 6.18 模块才能启动」。实测纠正：

- `ls /lib/modules` → **No such file**（出厂 Buildroot 不装 in-tree `/lib/modules`）
- 厂商 out-of-tree 模块在 `/system/lib/modules/`（`goodix.ko` / `8723ds.ko`，针对 4.19.232）
- 结论：6.18 的关键驱动（eMMC / ext4 / mmc / serial / 网络 PHY / USB2 / I2C）**全部内置（=y）**，
  所以无 `/lib/modules` 也能完整启动。
- ⚠️ 这也意味着：4.19 的 `goodix.ko` / `8723ds.ko` 因模块结构不匹配 6.18 → `invalid module format`，
  **不能**直接用于 6.18（需为 6.18 重编，见 `09_known_issues.md` Wi-Fi / 触摸）。

---

## 5. 后续：自己构建 64-bit rootfs（可选进阶）

若要彻底摆脱 32-bit 兼容包袱，可用 Buildroot 重新构建 **aarch64** rootfs 替换出厂分区。
但这超出当前 bring-up 范围；当前「64-bit kernel + 32-bit rootfs + CONFIG_COMPAT」已验证可用，
足以支撑学习 Linux 命令 / 系统构建的目标。
