# 排障 - Boot / 启动

> ⚠️ **历史路线（mainline-6.18）**：本页记录 mainline-6.18 阶段的排障，非当前现役路线。
> 现役路线是 Rockchip BSP 5.10，排障/状态见 `../porting/rockchip-5.10/`（`10_known_issues.md`、`11_debug_methodology.md`）。
> 6.18 特有结论（如 `ttyS2` 强制、`CONFIG_CMDLINE_FORCE`、FIT 外置头）不要直接套用到 5.10。

> 完整 6.18 启动日志见 `../porting/mainline-6.18/01_boot_chain.md` 与 `../porting/mainline-6.18/10_debug_notes.md`。

---

## 1. `FIT: No fit blob` / 启动卡在 U-Boot

**现象**：U-Boot 报 `FIT: No fit blob` 或直接不进内核。

**根因**：Rockchip U-Boot 的 `boot_fit` 调 `fit_is_ext_type()`，要求 FIT 头 `fdt_totalsize < 4KiB`。
普通 `mkimage -f`（内嵌数据）会把头撑到 ~14MiB，被拒。

**修复**：用**外置数据 FIT**：

```bash
mkimage -f fit-image.its -E -p 0x800 boot.img
# 自检：头必须 <0x1000 且 <=0x800
xxd -s 4 -l 4 boot.img     # 第 2 个 32 位 = totalsize，须 < 00001000
```

**参考**：`../porting/mainline-6.18/01_boot_chain.md` §一。

---

## 2. 内核解压后不启动 / 往非法地址搬

**现象**：`## Booting FIT Image` 反复失败。

**根因**：`.its` 用厂商占位符 `load/entry = 0xffffff01/0xffffff00`（仅 SPL 阶段有效），
手动 `boot_fit` 时 U-Boot 不换算 → 内核/设备树搬到非法地址。

**修复**：`.its` 用**真实 RAM 地址**：
- kernel `load/entry = 0x04080000`
- fdt `load = 0x08300000`

---

## 3. boot 分区装不下（>32MiB）

**现象**：39MiB 未压缩 `Image` 塞不进 32MiB boot 分区。

**修复**：内核 `.its` 设 `compression = "gzip"`，用 `Image.gz`（~14MiB）；
打包后安全截断：`truncate -s 32M boot.img`（先 `stat` 确认 <32M 再截，避免砍尾）。

---

## 4. 无串口输出（控制台静默）

**现象**：内核启动后串口无任何输出。

**根因**：bootargs 仍是厂内 `console=ttyFIQ0`（依赖 fiq-debugger，主线无此驱动）。

**修复**：内核强制 `console=ttyS2,1500000`：

```bash
./scripts/config --enable  CONFIG_CMDLINE_FORCE
./scripts/config --set-str CONFIG_CMDLINE "console=ttyS2,1500000 root=PARTUUID=614e0000-0000 rootwait"
```

---

## 5. VFS / rootfs 挂载失败

**现象**：`VFS: Unable to mount root fs`。

**排查**：
- 确认 `CONFIG_COMPAT=y`（出厂 rootfs 是 32-bit，见 `../porting/mainline-6.18/04_rootfs_compat.md`）。
- 确认 bootargs `root=PARTUUID=614e0000-0000 rootwait` 无误。
- 确认只烧了 `boot` 分区，没动 `rootfs` 分区。

> 实测：6.18 下 `[ 1.008170] VFS: Mounted root (ext4) on device 179:6` → `Run /sbin/init` 成功，
> 说明上述配置正确时 rootfs 挂载不是问题。

---

## 6. 启动后非致命报错（可进系统但报错）

见 `../porting/mainline-6.18/09_known_issues.md` §7：goodix/8723ds 版本错、屏不亮、configfs 缺失、
oem/userdata 挂载失败、`kvm` 组未知——均不阻止进系统。
